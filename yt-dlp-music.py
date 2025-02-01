# -*- coding: utf-8 -*-
"""
yt-dlp-music: YouTube動画のダウンロードと音声抽出を行うツール
"""
from dataclasses import dataclass
from configparser import ConfigParser
from typing import Optional, Dict, Any, Tuple
import json
import os
import re
import subprocess

DEFAULT_CONFIG = {
    'common': {
        'path': './out',
        'formatter': '%%(title)s.%%(ext)s',
        'path-check': 'true',
        'input': 'download_links_input.txt',
        'input-check': 'true'
    },
    'yt-dlp': {
        'type': 0,
        'exec': './yt-dlp/yt-dlp.exe',
        'options': '--progress --no-quiet --no-warnings --no-part --add-metadata --embed-thumbnail --convert-thumbnails jpg',
        'auto-update': 'true'
    },
    'ffmpeg': {
        'exec': './ffmpeg/ffmpeg.exe',
        'format': 'mp3',
        'bitrate': '192'
    },
    'playlist': {
        'range': '0'
    }
}
URL_PATTEN = r'^[a-zA-Z][a-zA-Z\d+\-.]*://(?:\w+\.)?\w+\.\w+(/.*)?$'
FILE_PATTEN = r'^.*\.[A-Za-z]{2,4}$'

class LogManager:
    def __init__(self):
        self._initial_messages()

    def _initial_messages(self):
        messages = [
            'yt-dlp-music Video Download Tool',
            'Copyright (C) 2023-2025 soburi. / test20140',
            ' ',
            'Copyright (c) 2000-2025 FFmpeg',
            'Copyright (c) 2023      mutagen',
            'Copyright (c) 2024      pycryptodome',
            ' '
        ]
        for msg in messages:
            self.info(msg)

    def debug(self, message: str) -> None:
        if message and message.replace('\n', '\\n'):
            if '[download]' in message:
                clean_message = message.replace('[DEBUG] ', '')
                # ダウンロードは1行で十分だから上書きで表示
                print(f"\r{clean_message}", end='', flush=True)
            else:
                clean_message = message.replace('[DEBUG] ', '')
                print(clean_message)

    def info(self, message: str) -> None:
        if message and message.replace('\n', '\\n'):
            if '[download]' in message:
                print(f"\r{message}", end='', flush=True)
            else:
                print(message)

    def warning(self, message: str) -> None:
        if message and message.replace('\n', '\\n'):
            print(f"[WARNING] {message}")

    def error(self, message: str) -> None:
        if message and message.replace('\n', '\\n'):
            print(f"[ERROR] {message}")

@dataclass
class Movie:
    """動画情報を保持するクラス。使うかもしれない"""
    title: str = 'DELETED MOVIE'
    url: str = ''
    uploader: str = ''
    duration: str = '0'
    pl_url: Optional[str] = None
    pl_title: Optional[str] = None

    @classmethod
    def from_info(cls, info_dict: Dict[str, Any], playlist_info: Optional[Dict[str, Any]] = None) -> 'Movie':
        if not info_dict:
            return cls()
        
        return cls(
            title=info_dict.get('title', 'DELETED MOVIE'),
            url=info_dict.get('original_url', ''),
            uploader=info_dict.get('uploader', ''),
            duration=info_dict.get('duration_string', '0'),
            pl_url=playlist_info.get('webpage_url') if playlist_info else None,
            pl_title=playlist_info.get('title') if playlist_info else None
        )

class YTDLPManager:
    """yt-dlpの操作を管理するクラス"""
    # TODO: オブジェクト指向でやると管理しやすいかもしれない
    def __init__(self, config: str, ffmpeg_config: Dict[str, Any], type: int, exec: str):
        self.options = config
        self.type = int(type)
        self.exec = exec
        self._setup_options(ffmpeg_config)
        if self.type == 1:
            import yt_dlp
            self.ydl = yt_dlp.YoutubeDL(self.options)

    def _setup_options(self, ffmpeg_config: Dict[str, Any]) -> None:
        """yt-dlpのオプションを設定"""
        if self.type == 0:
            if ffmpeg_config.get('format'):
                self.options += " --format ba"
                self.options += " --format-sort abr,acodec"
                self.options += " --format-sort-force"
                self.options += " --extract-audio"
                self.options += " --audio-format "+ffmpeg_config['format']
                self.options += " --audio-quality "+ffmpeg_config.get('bitrate', '192')
                self.options += " --ffmpeg-location "+ffmpeg_config['exec']

        elif self.type == 1:
            self.options = json.loads(self.options)
            if ffmpeg_config.get('format'):
                self.options["format"] = "ba"
                self.options["format_sort"] = ["abr", "acodec"]
                self.options["format_sort_force"] = True
                self.options.setdefault('postprocessors', []).extend([{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': ffmpeg_config['format'],
                    'preferredquality': ffmpeg_config.get('bitrate', '192')
                }])
            self.options.update({
                'logger': log_manager,
                'ffmpeg_location': ffmpeg_config['exec']
            })

    def download(self, url: str, playlist_range: Optional[Tuple[int, int]] = None) -> None:
        """URLからダウンロードを実行"""
        # TODO: Pipeを利用したダウンロード　エラー発生時に一時ファイルを自動削除
        if self.type == 0:
            options = self.options
            if playlist_range:
                start, end = playlist_range
                options += f' --playlist-items {start}-{end}'
            result = subprocess.Popen(self.exec +" "+ options +" "+ url, stdout=subprocess.PIPE, text=True)
            while result.poll() == None:
                line = result.stdout.readline()
                log_manager.info(line.strip())
            result.wait()
            if not result.returncode == 0:
                log_manager.info("Error during download: except 0")

        elif self.type == 1:
            options = self.options.copy()
            if playlist_range:
                start, end = playlist_range
                options['playlist_items'] = f'{start}-{end}'
            try:
                self.ydl.download([url])
            except Exception as e:
                log_manager.error(f"Error during download: {str(e)}")

    def is_playlist(self, url: str) -> bool:
        """URLがプレイリストかどうかを判定"""
        if "list=" in url:
            return True
        else:
            return False

    def update(self) -> None:
        """yt-dlpの更新を実行"""
        code = 0
        try:
            if self.type == 0:
                result = subprocess.run([self.exec, "-U"], capture_output=True, text=True)
                code = result.returncode
            elif self.type == 1:
                import yt_dlp
                yt_dlp.update.Updater(self.ydl).update()
                code = 0
            if code == 0:
                log_manager.info(f"{'YT-DLP Update':20} Check {'':8}  OK")
            else:
                log_manager.error(f"{'YT-DLP Update':20} Check {'':8}  ERROR")
        except Exception as e:
            log_manager.warning(f"Error checking yt-dlp update: {str(e)}")

    def params(self, key, value):
        if self.type == 0:
            options = str(self.options)
            start = options.find(key)
            if start == -1:
                self.options = options +" "+key+" "+value
                return
            end = options.find('--', start + len(key))
            if end == -1:
                end = len(options)
            self.options = options[:start-1] + options[end+1:] +" "+key+" "+value

        elif self.type == 1:
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

def load_config(file_path: str) -> Dict[str, Any]:
    """設定ファイルを読み込む"""
    if not os.path.exists(file_path):
        create_default_config(file_path)
    
    config = ConfigParser()
    config.read(file_path, encoding='utf-8')
    
    return {
        'common': {
            'path': config.get('common', 'path', fallback=DEFAULT_CONFIG['common']['path']),
            'formatter': config.get('common', 'formatter', fallback=DEFAULT_CONFIG['common']['formatter']),
            'path-check': config.getboolean('common', 'path-check', fallback=DEFAULT_CONFIG['common']['path-check']),
            'input': config.get('common', 'input', fallback=DEFAULT_CONFIG['common']['input']),
            'input-check': config.getboolean('common', 'input-check', fallback=DEFAULT_CONFIG['common']['input-check'])
        },
        'yt-dlp': {
            'type': config.getint('yt-dlp', 'type', fallback=DEFAULT_CONFIG['yt-dlp']['type']),
            'exec': config.get('yt-dlp', 'exec', fallback=DEFAULT_CONFIG['yt-dlp']['exec']),
            'options': config.get('yt-dlp', 'options', fallback=DEFAULT_CONFIG['yt-dlp']['options']),
            'auto_update': config.getboolean('yt-dlp', 'auto-update', fallback=DEFAULT_CONFIG['yt-dlp']['auto-update'] == 'true')
        },
        'ffmpeg': {
            'exec': config.get('ffmpeg', 'exec', fallback=DEFAULT_CONFIG['ffmpeg']['exec']),
            'format': config.get('ffmpeg', 'format', fallback=DEFAULT_CONFIG['ffmpeg']['format']),
            'bitrate': config.get('ffmpeg', 'bitrate', fallback=DEFAULT_CONFIG['ffmpeg']['bitrate'])
        },
        'playlist': {
            'range': config.get('playlist', 'range', fallback=DEFAULT_CONFIG['playlist']['range'])
        }
    }

def create_default_config(file_path: str) -> None:
    """デフォルトの設定ファイルを作成"""
    config = ConfigParser()
    for section, settings in DEFAULT_CONFIG.items():
        config[section] = settings
    with open(file_path, 'w', encoding='utf-8') as f:
        config.write(f)

def check_ffmpeg(ffmpeg_path: str) -> None:
    """FFmpegの存在確認とバージョンチェック"""
    try:
        result = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            log_manager.info(f"{'FFmpeg':20} Check {'':8}  OK")
        else:
            log_manager.error(f"{'FFmpeg':20} Check {'':8}  ERROR")
    except Exception as e:
        log_manager.warning(f"Error checking FFmpeg: {str(e)}")

def get_playlist_range(range_config: str) -> Optional[Tuple[int, int]]:
    """プレイリストの範囲を取得"""
    while True:
        log_manager.info(f"Enter playlist range (e.g., 1-10, all videos for 0, Press 'Enter' for setting.ini→{range_config})")
        range_input = input(f"Playlist range > ").strip() or range_config
        
        if range_input == '0' or range_input.lower() == 'all':
            return None
            
        match = re.match(r'^(\d+)-(\d+)$', range_input)
        if match:
            start, end = map(int, match.groups())
            if start <= end:
                return (start, end)
                
        log_manager.warning("Invalid range format. Please enter '0' for all videos or use format like '1-10'")

def get_links_input(path: str) -> []:
    """ファイルからurl一覧を取得"""
    lst = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            lst.append(line.strip())
    return lst

def fls_con() -> None:
    """コンソールのバッファ削除"""
    if os.name == 'nt':
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    elif os.name == 'posix':
        import select
        while select.select([sys.stdin.fileno()], [], [], 0.0)[0]:
            os.read(sys.stdin.fileno(), 4096)


def main():
    # 設定ファイルの読み込み
    config = load_config('setting.ini')
    #log_manager.debug(f"Loaded configration file. {config}\n")
    
    # FFmpegの確認
    check_ffmpeg(config['ffmpeg']['exec'])
    
    # YT-DLPマネージャーの初期化
    ytdlp = YTDLPManager(
        config['yt-dlp']['options'],
        config['ffmpeg'],
        config['yt-dlp']['type'],
        config['yt-dlp']['exec']
    )

    # YT-DLPの更新
    if config['yt-dlp']['auto_update']:
        ytdlp.update()

    _path = config['common']['path']
    _url = config['common']['input']
    while True:
        try:
            fls_con()
            # 対話
            if config['common']['path-check']:
                log_manager.info(f"\nEnter directory location or Press Enter to use {_path}")
                path = input("Location >").strip() or _path
                if path.lower() == 'exit':
                    break
            if config['common']['input-check']:
                log_manager.info(f"\nEnter YouTube URL (playlist or video link) or Press Enter to use {_url}")
                url = input("URL >").strip() or _url

            formatter = config['common']['formatter']
            lst = []
            # 整理
            if config['yt-dlp']['type'] == 0:
                ytdlp.params('--output', os.path.join(path, formatter))
            elif config['yt-dlp']['type'] == 1:
                outtmpl = {
    		        'default': os.path.join(path, formatter), 
                    #'chapter': os.path.join(path, '%(title)s - %(section_number)03d %(section_title)s [%(id)s].%(ext)s') 
                }
                ytdlp.params(['outtmpl'], outtmpl)

            if (re.match(FILE_PATTEN, url)):
                lst = get_links_input(url)
            elif (re.match(URL_PATTEN, url)):
                lst = [url]
            elif (url.lower() == 'exit'):
                break
            else:
                log_manager.error("Invalid url/path")
                continue

            for mov in lst:
                if mov.lower() == 'exit':
                    break
                if ytdlp.is_playlist(mov):
                    range_tuple = get_playlist_range(config['playlist']['range'])
                    ytdlp.download(mov, range_tuple)
                else:
                    ytdlp.download(mov)
        except KeyboardInterrupt:
            log_manager.warning("Operation cancelled by user")
            break
        except:
            log_manager.error(f"An error occurred")
            import traceback
            traceback.print_exc()

    log_manager.info("yt-dlp-music is shutting down")

if __name__ == "__main__":
    print("Please wait...\n")
    log_manager = LogManager()
    main()
