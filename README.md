## youtubeの動画をyt-dlpを使って音声としてダウンロードするスクリプト

ダウンロードはこちらを実行してください。
```
git clone https://github.com/soburi59/yt-dlp-music.git
```

 ### 準備: 依存関係の解決
このスクリプトはyt-dlpとffmpeg(ffprobe)が必要です。  
デフォルトでは、exeファイルを使用するように設定されています。  
<br/>

1. **yt-dlp**

yt-dlpディレクトリに同梱済みです。  
ダウンロードする必要はありません。

2. **ffmpeg**

以下のリンクからダウンロードするか、ビルドしてください。  
[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

解凍し、ffmpegディレクトリ以下に格納します。  
すでにffmpegがある場合は、setting.ini内の`[ffmpeg]` `exec`にパスを設定してください。(現在同梱を検討しています)

<!-- 1. yt-dlp  
以下のリンクからダウンロードしてください。  
[https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe)

解凍し、yt-dlpディレクトリ以下に格納します。  
すでにyt-dlpがある場合は、setting.ini内の`[yt-dlp]` `exec`にパスを設定してください。  


2. ffmpeg  
以下のリンクからダウンロードするか、ビルドしてください。  
[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

解凍し、ffmpegディレクトリ以下に格納します。  
すでにffmpegがある場合は、setting.ini内の`[ffmpeg]` `exec`をそのパスに設定してください。  -->


### 使用方法
exeのショートカットを適当な場所に作成して実行します。  
ダウンロード先のディレクトリ、urlを順に指定してダウンロードします。  
download_links_input.txtにダウンロードしたい動画のurlを改行区切りで記載することで複数の動画をダウンロードすることもできます。

<hr>

### 使用上の注意  

> **Warning**  
> youtubeに上がっているものをダウンロードするのはyoutubeの規約違反ですから自己責任です。  
> 違法アップロードをしてある動画をダウンロードするのは、私的利用に関わらず著作権法に抵触します。  
> 公式が上げている(アーティスト本人など)ものをダウンロードするのは規約違ですが法的に問題はありません。  
> 再配布は著作権法に抵触します。  
> 以上のことを踏まえて使用してください。  
<br/>

> **Note**  
> エラーによりダウンロードができない場合、setting.ini内の`auto-update`を`True`に変更するか、以下のコマンドを実行してください。  
> `yt-dlp.exe -U`
<br/>

> **Note**  
> このプログラムは、yt-dlpをexeとpythonからの呼び出しの両方から動作させる事が可能です。  
> また、このスクリプトのexe版にはyt-dlpがすでに組み込まれていますから、setting.iniの`[yt-dlp]` `type`および`[yt-dlp]` `options`を変更することで、pythonからの呼び出しに変更できます。(ffmpegは別途用意が必要です)

<hr>

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

#### 謝辞
以下のライブラリー・ソフトウェアを使用させていただきました。
- yt-dlp
- mutagen
- pycryptodome
- FFmpeg及びffmpeg関連のコーデック

この場を借りて感謝申し上げます。
