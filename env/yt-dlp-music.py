# -*- coding: utf-8 -*-
"""
Created on 2023/4/4

@author: soburi
"""
import sys, os,subprocess
while(True):
    path='.'
    #path.txtに記載してあるパスに保存
    try:
        with open('path.txt',mode='r') as f:
            path = f.readline()
    except:
        print('nothing text file')
        sys.exit()
    
    url=input("youtube url(list ok):")
    if "list=" in url:
        end = int(input("end-list(example:3→download the three lastest music):"))
        cmd = f"yt-dlp.exe -x -f ba -i --parse-metadata 'artist:%(channel)s' -o {path:s}/%(title)s.%(ext)s --playlist-end {end} --add-metadata --audio-format mp3 "+url
    else:
        cmd = f"yt-dlp.exe -x -f ba -i --parse-metadata 'artist:%(channel)s' -o {path:s}/%(title)s.%(ext)s --add-metadata --audio-format mp3 "+url
    subprocess.run('echo '+cmd,shell=True)
    subprocess.run(cmd,shell=True)