## youtubeの動画をyt-dlpを使って音声としてダウンロードするスクリプト
exeだけダウンロードしても動かないのでクローンするように.   

```
git clone https://github.com/soburi59/yt-dlp-music.git
```

## 準備:ffmpegのダウンロード&格納
[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
解凍し、ffmpegディレクトリ以下に格納.  
すでにffmpegがある場合は、そのパスをsetting.iniのffmpegのexecに設定してください.  

## 使用方法
exeのショートカットを適当な場所に作成して実行.
download_links_input.txtにダウンロードしたい動画のurlを改行区切りで記載することで複数の動画をダウンロードすることもできます.

## 使用上の注意  

> **Warning**
> youtubeに上がっているものをダウンロードするのは規約違反なので自己責任.  
> 違法アップロードをしてあるものを知ってダウンロードするのは違法.  
> 公式が上げている(アーティスト本人など)ものをダウンロードするのは規約違反だが違法ではない.再配布はもちろん違法.  
> 以上のことを踏まえて使用すること.

> **Note** 
> エラーでダウンロードできないときはyt-dlpフォルダ内のyt-dlp.exeを以下サイトからダウンロードして差し替えてください.
> https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe
> 
>  
#### 更新
2023/4/5 自分の環境でしか動かなかったのでちゃんと動くようにしました ffmpegとyt-dlpのexeを入れています
2023/6/5 ありがたいことに改良してくれましたので https://github.com/FoxxCool/yt-dlp-music-fork を採用
2023/6/5 少し変更(コンマでなく改行区切りで読み込むように,表示をわかりやすく,入力なしでmusic.txtを読み込むように)
2024/12/29 大幅に変更(設定ファイルをiniに変更,ダウンロードリンクのファイルをdownload_links_input.txtに変更)

#### 詳細
プログラムを改変した場合は以下を実行
```
pipenv install
pyinstaller --onefile yt-dlp-music.py
```

