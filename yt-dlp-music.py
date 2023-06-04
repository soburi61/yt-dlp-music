# -*- coding: utf-8 -*-
"""
Created on 2023/4/4
Edited on 2023/4/17
Changed on 2023/6/5
@author: soburi
"""
import sys, subprocess
while(True):
    path = input("(Default:[Enter] →~/Music/Music)\nTarget path:") or "~/Music/Music"

    if (path == "end"):
        break

    url = input("(play list url ok)\n(Default:[Enter]→import music.txt)\nmovie url:")
    cmd = f".\yt-dlp\yt-dlp.exe --ffmpeg-location ./ffmpeg/ffmpeg.exe --parse-metadata artist:%(channel)s -o {path:s}/%(title)s -f b --add-metadata --extract-audio --embed-thumbnail --audio-format mp3 "
    
    list = []
    if "https://" in url:
        tmp = url
        if "list=" in url:
            #TODO: もしlistだけではなくvideoも指定してしまっていたら正規表現など使って改変を行う。 (ニコニコなども考慮する)
            end = int(input("(example:3→download the 3 lastest music)\n(Default:[Enter]→download all)\n end num:") or 0)
            if end != 0:
                tmp = f"--playlist-end {end} --yes-playlist {url}"
        list.append(tmp)

    else:
        try:
            with open('music.txt', mode='r') as f:
                list = f.readlines()
        except:
            print("nothing text file.")
            sys.exit(1)
    
    for urls in list:
        subprocess.run('echo '+cmd+urls, shell=True)
        subprocess.run(cmd+urls, shell=True) 
    
