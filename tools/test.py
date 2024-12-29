from yt_dlp import YoutubeDL
with YoutubeDL({'ffmpeg_location': './ffmpeg/ffmpeg.exe'}) as ydl:
	ydl.download('https://www.nicovideo.jp/watch/sm9')