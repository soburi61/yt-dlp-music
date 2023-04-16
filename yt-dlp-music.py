# -*- coding: utf-8 -*-
"""
Created on 2023/4/4
Edited on 2023/4/17

@author: soburi
"""
import sys, os,subprocess
while(True):
    path = input("Target path (Default ~/Music): ") or "~/Music"

    if (path == "end"):
        break

    url = input("movie url(play list & text file ok): ")
    cmd = f".\yt-dlp\yt-dlp.exe -x -f ba -i --ffmpeg-location ./ffmpeg/ffmpeg.exe --parse-metadata artist:%(channel)s -o {path:s}/%(title)s.%(ext)s -f b --add-metadata --audio-format mp3 "
    
    list
    if "https://" in url:
        tmp = url
        if "list=" in url:
            #TODO: もしlistだけではなくvideoも指定してしまっていたら正規表現など使って改変を行う。 (ニコニコなども考慮する)
            end = int(input("end-list example:3→download the three lastest music 0→download the all music (default): ") or 0)
            if end != 0:
                tmp = f"--playlist-end {end} {url}"
        list = {tmp}

    elif ".txt" in url:
        try:
            with open(url, mode='r') as f:
                list = f.readline().split(",")
        except:
            print("nothing text file.")
            sys.exit(1)
    
    for urls in list:
        subprocess.run('echo '+cmd+urls, shell=True)
        subprocess.run(cmd+urls, shell=True)
