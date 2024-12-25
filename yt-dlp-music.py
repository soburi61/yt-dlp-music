# -*- coding: utf-8 -*-
"""
Created on 2023/4/4
Edited on 2023/4/17
Changed on 2024/12/25
@author: soburi
"""
#TODO: YT-DLPとFFMPEGの同時実行, プレイリストの場合マルチスレッドで処理, コマンドのみでのYT-DLPの実行, メタデータ(ジャンル等々)+動画ファイル管理 music.txtでディレクトリ指定(複数可) クラス化
from dataclasses import dataclass, field, fields, asdict
from concurrent.futures import ThreadPoolExecutor
from configparser  import ConfigParser, NoOptionError
from typing import Type, List
import sys
import yt_dlp
#pycryptodome, mutagen
import json
import os
import re
import subprocess
import threading
import math
import time

print('YT-DLP-MUSIC 動画作品 ﾀﾞｳﾝﾛｰﾄﾞ ﾂｰﾙ')
print('Copyright (C) 2023,2024 soburi. / test20140')
print()
print('Copyright (c) 2000-2024 FFmpeg')
print('Copyright (c) 2023      mutagen')
print('Copyright (c) 2024      pycryptodome')
print()

url_patten = r'^[a-zA-Z][a-zA-Z\d+\-.]*://(?:\w+\.)?\w+\.\w+(/.*)?$'
file_patten = r'^.*\.[A-Za-z]{2,4}$'

# Movie Data
class Movie:
	def __init__(self, _info=None, pl=None, entries_num=None):
		if pl == None:
			pl = {}
		self.pl_url = pl.get('webpage_url', None)
		self.pl_title = pl.get('title', None)
		self.pl_uploader = pl.get('uploader', None)
		self.pl_extractor = pl.get('extractor_key', None)
		self.pl_order = entries_num
		if _info == None:
			info = {}
		else:
			info = _info['info_dict']
		self.title = info.get('title', 'DELETED MOVIE')
		self.url = info.get('original_url', '')
		self.uploader = info.get('uploader', '')
		self.description = info.get('description', '')
		self.duration = info.get('duration_string', '0')
		self.formats = info.get('formats', [])
		self.headers = info.get('http_headers', {})
		self.cookies = info.get('cookies', None)
		self.ie = info.get('ie_key', None)

# Configuration Base Data
@dataclass
class _base:
	@property
	def section(self) -> str:
		raise NotImplementedError

#Configuration Data
# section common in configuration
@dataclass
class __common(_base):
	@property
	def section(self) -> str: 
		return "common"
	path: str = "~/Music" # The Directory name of "default" to download
	file: str = "./music.txt" # The File name of "default" to read a url list 
	ansi: bool = True # Enable to use ANSI

# section yt-dlp in configuration
@dataclass
class __yt_dlp(_base):
	@property
	def section(self) -> str: 
		return "yt-dlp"
	type: int = 0 # The type of Yt-dlp's library 
	options: dict = field(default_factory=lambda: {"noprogress": False, "logger": None, "quiet": True, "no_warnings":True, "writethumbnail": True, "postprocessors": [{"key": "FFmpegMetadata", "add_metadata": True},{"key": "EmbedThumbnail", "already_have_thumbnail": False},{"format": "jpg", "key": "FFmpegThumbnailsConvertor","when": "before_dl"}]}) # The options of Yt-dlp (make sure https://github.com/yt-dlp/yt-dlp#usage-and-options)
	auto_update: bool = True # Enable to auto update

# section ffmpeg in configuration
@dataclass
class __ffmpeg(_base):
	@property
	def section(self) -> str: 
		return "ffmpeg"
	exec: str = "./ffmpeg/ffmpeg.exe" # The location of FFmpeg
	format: str = "mp3" # The audio format type
	bitrate: str = ""


# Configuration
# Note that in the Configuration class, the "-" in config's key is replaced "_".
class Configuration:
	def __init__(self, path: str, types: List[Type[_base]]):
		self.path = path
		self.types = types
		if not (self.is_exists()):
			self.default(self.path)
		self.ini = ConfigParser()

	def is_exists(self):
		return os.path.exists(self.path)

	def default(self, path):
		 self.write(path, ConfigParser())

	def load(self):
		self.read(self.path)
		confs = []
		for struct in self.types:
			r = struct()
			self._model(r, self.ini)
			confs.append(r)
		return confs;

	def write(self, path: str, ini: ConfigParser):
		for struct in self.types:
			conf = struct()
			section = conf.section
			data = asdict(conf)
			ini[section] = {k.replace("_", "-"): json.dumps(v) if isinstance(v, dict) else str(v) for k, v in data.items()}
		with open(path, 'w', encoding='utf-8') as file:
			ini.write(file)

	def read(self, path):
		self.ini.read(path, encoding='utf-8')

	def _model(self, r: _base, ini: ConfigParser):
		section = r.section
		for _k in list(vars(r).keys()):
			if _k == section:
				continue
			attr = type(getattr(r, _k))
			k = _k.replace("_", "-")
			try:
				if attr is int:
					value = ini.getint(section, k)
				elif attr is float:
					value = ini.getfloat(section, k)
				elif attr is bool:
					value = ini.getboolean(section, k)
				elif attr is dict:
					value = json.loads(ini.get(section, k))
				elif attr is str:
					value = ini.get(section, k)
				setattr(r, _k, value)
			except NoOptionError:
				print(ini.get(section, k))
				print(f'Error: 設定ﾌｧｲﾙの解析中にｴﾗｰが発生しました｡')

# For count the active threads
class _Executor(ThreadPoolExecutor):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.lock = threading.Lock()
		self.active_threads = 0
		self.task_done = False

	def submit(self, fn, *args, **kwargs):
		with self.lock:
			self.active_threads += 1
		future = super().submit(self._wrap_task, fn, *args, **kwargs)
		return future

	def _wrap_task(self, fn, *args, **kwargs):
		try:
			return fn(*args, **kwargs)
		finally:
			with self.lock:
				self.active_threads -= 1
				if self.active_threads == 0:
					self.task_done = True

	# number of threads
	def get_threads(self):
		with self.lock:
			return self.active_threads


lst  = [] # processing
_lst = [] # finished
urls = [] # entries
errs = [] # error

class yt_dlp_manage():
	def __init__(self, conf):
		self.conf = conf
		self._options = conf.options
		self.ydl = yt_dlp.YoutubeDL(self._options)
		self._extractors = yt_dlp.extractor.gen_extractor_classes()
		self.yt_dlp_ = _Executor(max_workers=1)
		self.hook = False

	def _get_extractor(self, url):
		for extractor_class in self._extractors:
			extractor = extractor_class()
			if extractor.suitable(url):
				return extractor
		return None

	# File
	def loads(self, file, b=False):
		with open(file, mode='r') as f:
			line = f.readlines()
			for url in line:
				_urls = []
				if (re.match(file_patten, url)):
					urls.extend(loads(_urls, True))
				urls.append(url)
				if b:
					return _urls
		for url in urls:
			self.download(url, file)

	# Moive or Playlist
	def download(self, url, file=None):
		if not file:
			urls.append(url)
		try:
			self.ydl.download([url])
		except:
			errs.append(url)

	# Update infomation
	def p(d):
		global lst
		obj = _s_attribute(_lst, 'url', d['info_dict']['original_url'])
		if (len(obj) == 0):
			movie = Movie(d)
			lst.append(movie)
			_lst.append(movie)
		elif (d['status'] == 'finished'): # どうやらダウンロードと画像処理で二回トリガーされるらしい
				if obj[0] in lst:
					lst.remove(obj[0])

	def update(self):
		yt_dlp.update.Updater(self.ydl).update()

	def params(self, key, value):
		_s_neste(self.ydl.params, key, value)
		self.ydl._parse_outtmpl()

def _s_neste(dic, keys, value):
	key = keys[0]
	if len(keys) == 1:
		dic[key] = value
	else:
		if key not in dic:
			dic[key] = {}
		_s_neste(dic[key], keys[1:], value)


def _s_attribute(objs, key, value):
	return list(filter(lambda obj: getattr(obj, key) == value, objs))

# If may recognize as unicode, convert to string
def unicode_esc(str):
	if re.search(r'\\u[0-9a-fA-F]{4}', str): 
		res = str.encode('unicode-escape').decode()
	else:
		res = str
	return res;

# Convert to ms/秒/分・秒/時間・分・秒 form epoch
def format_time(epoch):
	now = time.time()
	if (epoch == 0):
		return now;
	res = round(now - epoch, 3)

	if(res < 1): # milisecound
		return f"{math.floor(res*1000)}ms"
	elif(res < 60): # secound
		return f"{round(res, 1)}秒"
	elif(res < 60*60): # mintens
		min = math.floor(res / 60)
		sec = round(res % 60)
		return f"{min}分 {sec}秒"
	else: # hours or aonther
		hour = math.floor(res / 3600)
		min = math.floor((res % 3600) / 60)
		sec = round(res / 60)
		return f"{hour}時間 {min}分 {sec}秒"

# Formatted string
def formatting(str, *array):
	print(str.format(*array))

# ANSI CODE
# https://wikipedia.org/wiki/ANSI_escape_code
CHA = "\033[G" # Cursor Horizontal Absolute
CPL = "\033[1F" # Cursor Previous Line
EL   = "\033[2K" # Erase in Line
# Back Line
def backline(num):
	sys.stdout.write(EL)
	if num == 1:
		sys.stdout.write(EL+CHA)
	elif num > 1:
		for i in range(num):
			sys.stdout.write(CPL+EL)
	sys.stdout.flush()


# Main method
def main():
	# Load Configuration
	file = 'setting.ini'
	types = [__common, __yt_dlp, __ffmpeg] 
	conf = Configuration(file, types) 
	(_common, _yt_dlp, _ffmpeg) = conf.load()
	# Configuration Check
	count = sum([len(fields(struct)) for struct in types])
	formatting("{0:20} Check {1:8}  {2}", "Configuration", f"{count}keys", "OK")

	#FFMPEG
	res = subprocess.run([_ffmpeg.exec, "-version", ""], capture_output=True, text=True)
	formatting("{0:20} Check {1:8}  {2}", "FFmpeg", "", "OK" if res.returncode == 0 else "ERROR")
	print()

	print(f"動画転送ｼｽﾃﾑYT-DLP Ver {yt_dlp.version.__version__}")
	print("Since 2006 yt-dlp / youtube-dl ｺﾐｭﾆﾃｨ")
	opts = {
		"outtmpl": _common.path,
		"ffmpeg_location": _ffmpeg.exec,
		"progress_hooks": [yt_dlp_manage.p]
	}
	if not (_ffmpeg.format == ""):
		#opts.update({"format": "bestaudio", "format_sort_force": "", "format_sort": ["abr", "acodec"]})
		if not (_ffmpeg.bitrate == ""):
			bitrate = _ffmpeg.bitrate
		opts.update({"postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": _ffmpeg.format, "preferredquality": _ffmpeg.bitrate}]})
	_yt_dlp.options.update(opts)
	ytdlp = yt_dlp_manage(_yt_dlp)
	print("YT-DLPをｼｽﾃﾑに組み込みました.")

	# Check Updates
	if (_yt_dlp.auto_update):
		print("更新を取得します.")
		ytdlp.update()
		print("完了しました.")

	# Start console
	while True:
		global urls
		global errs
		global lst
		global _lst
		urls = []
		errs = []
		lst  = []
		_lst = []
		print()
		print(f"ﾃﾞﾌｫﾙﾄ値 PATH: {_common.path} URL: {_common.file} が<ｴﾝﾀｰ>で利用できます.\n")
		print("<ctl+c>でｷｬﾝｾﾙ, endで終了できます.\n")
		# Flush the stdin
		# https://stackoverflow.com/questions/2520893/how-to-flush-the-input-stream
		if os.name == 'nt':
			import msvcrt
			while msvcrt.kbhit():
				msvcrt.getch()
		elif os.name == 'posix':
			import select
			while select.select([sys.stdin.fileno()], [], [], 0.0)[0]:
       			 os.read(sys.stdin.fileno(), 4096)
		try:
			path = input(f"PATH >") or _common.path
			if (path == "end"):
				break
		except KeyboardInterrupt:
			if (_common.ansi):
				backline(5)
				continue;
		print(f"PATHに\"{path}\"を設定します.")
		outtmpl = { 
			'default': os.path.join(path, '%(title)s.%(ext)s'), 
			'chapter': os.path.join(path, '%(title)s - %(section_number)03d %(section_title)s [%(id)s].%(ext)s') 
		}
		ytdlp.params(['outtmpl'], outtmpl)
		try:
			file = input(f"URL >") or _common.file
			if (file == "end"):
				break
		except KeyboardInterrupt:
			if (_common.ansi):
				backline(7)
				sys.stdout.flush()
				continue;
		print(f"URLに\"{file}\"を設定します.")

		n_s = format_time(0)
		print("処理を開始します. ")

		all_done = threading.Event()
		loader = _Executor(max_workers=1)
		futures = []

		if (re.match(file_patten, file)):
			#File
			futures.append(loader.submit(ytdlp.loads, file))
		elif (re.match(url_patten, file)):
			# Movie or Playlist
			futures.append(loader.submit(ytdlp.download, file))
		else:
			print('Error: 認識できないurlです.')
			continue;

		t = format_time(0)
		p = 0
		movie = Movie()
		while loader.get_threads() > 0:
			if len(lst) == 0:
				disp = '待機中...'
				duration = ''
				pl = ''
				lenght = ''
			else:
				if not (movie.url == lst[len(lst)-1].url):
					p = 0
				movie = lst[len(lst)-1]
				title = list(movie.title)
				if len(title) > 10:
					disp = ' '.join(s for s in (title[(p % len(title)):10 + p % len(title)]))
				else:
					disp = "".join(title)
				duration = movie.duration
				pl = ",p" if not movie.pl_url==None else ""
				lenght = f'...他{len(lst)-1}'
			print("==================================================")
			formatting("処理中の動画: {0:20} ({1}{2}) {3}", disp, duration, pl, lenght)
			formatting("実行中のｽﾚｯﾄﾞ: {0:2}", loader.get_threads())
			formatting("処理の動画数: {0:3}/{1:3}　進行時間: {2:10}", len(_lst)+len(errs), len(urls), (format_time(t)))
			msg = "== しばらくお待ちください . =="
			if (p % 3 == 1):
				msg = "= しばらくお待ちください . . ="
			if (p % 3 == 2):
				msg = " しばらくお待ちください . . . "
			print(f"=================={msg}==")
			p+=1;
			time.sleep(1)
			backline(5)
		results = [future.result() for future in futures]
		lst = []
		print()
		print(f"全ての処理が完了しました. ({format_time(n_s)})")
		print("==================================================")
		formatting("動画数... 総動画数: {0:3}", len(_lst)+len(errs))
		formatting("　　　　  成功: {0:3} 失敗: {1:2}", len(_lst), len(errs))
		formatting("処理時間: {0}", format_time(n_s))
		print("=================== ご利用ありがとうございます ==")

if __name__ == "__main__":
    main()

print("YT-DLP-MUSICを終了します。")

