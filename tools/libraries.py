import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

tr = []
libs = []

print()
print("================= Formats =========================")
print()

# get supported Formats
url = 'https://ffmpeg.org/general.html'

res = requests.get(url)
soup = BeautifulSoup(res.content, 'lxml')

_tables = soup.find_all('table')
file  = pd.read_html(str(_tables[0]))[0]
img   = pd.read_html(str(_tables[1]))[0]
video = pd.read_html(str(_tables[2]))[0]
audio = pd.read_html(str(_tables[3]))[0]
subt  = pd.read_html(str(_tables[4]))[0]
net   = pd.read_html(str(_tables[5]))[0]
for table in [file, img, video, audio, subt, net]:
	for _, row in table.iterrows():
		if (row[0] == "Name"):
			continue;
		strs = [row[0]]
		if ("/" in row[0].strip()):
			strs = row[0].split("/")
		for str in strs:
			tr.append(str)

print(tr)

print()
print("================= Libraries =========================")
print()

# get supported liraries
url = 'https://raw.githubusercontent.com/FFmpeg/FFmpeg/refs/heads/master/configure'

res = requests.get(url)
lines = res.text.split('\n')

started = False
started_l = 0
for line in lines:
	if 'External library support:' == line:
		started = True
		continue
	if started:
		if line.strip() == '':
			started_l+=1
			if started_l > 4:
				break
		match = re.match(r'--enable-([\w-]+)', line.strip())
		if match:
			libs.append(match.group(1))

print(libs)

print()
print("================= FFmpeg.py =========================")
print()

# get yt_dlp's ffmpeg.py
url = 'https://raw.githubusercontent.com/yt-dlp/yt-dlp/refs/heads/master/yt_dlp/postprocessor/ffmpeg.py'

res = requests.get(url)
lines = res.text.split('\n')

n_lib = []
n_ext = []

# Check
for i, line in enumerate(lines, start=1):
	if line.strip().startswith('#'):
		continue;
	for lib in libs:
		if lib.lower() in line.lower():
			print(f"{i}: {line}  ==  {lib}")
			n_lib.append(lib)
	for ext in tr:
		if re.search(r'\b' + re.escape(ext.lower()) + r'\b', line.lower()):
			print(f"{i}: {line}  ==  {ext}")
			n_ext.append(ext)

lib = list(set(n_lib))
ext = list(set(n_ext))

# Result
print()
print("================= Results =========================")
print(f" Require Libs: {lib}")
print(f" Require Exts: {ext}")

# Require Libs: ['libvorbis', 'libopus', 'libmp3lame', 'libxvid', 'libfdk-aac']
# Require Exts: ['ASS', 'TTML', 'MP4', 'Matroska', 'Ogg', 'AAC', 'WebP', 'MP3', 'MOV', 'WebVTT', 'AVI', 'Vorbis', 'Opus', 'WAV', 'WebM', 'pipe', 'ASF', 'JPEG'] (https, http, file)
