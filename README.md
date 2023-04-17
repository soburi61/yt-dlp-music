## youtubeの動画をyt-dlpを使って音声としてダウンロードするスクリプト
exeだけダウンロードしても動かないのでクローンするように.  

```
git clone https://github.com/soburi59/yt-dlp-music.git
```

クローンしたらダブルクリックで使えます.<br />
保存場所は最初に`Target path`と聞かれますのでお好みの場所を選択してください.<br />
デフォルトではユーザーのミュージックの中にMusicフォルダを作りそこの中に保存します.<br />

次に`movie url`と聞かれますので動画のurlやurlをコンマ区切りで管理しているファイルを選択してください。<br />
<br>
再生リストのurlを入力した場合,再生リストのどこまでをダウンロードするかを聞かれます.  <br />
(youtubeなどのプレイリストは動画idを含めてしまうと、正常に作動しません。  
そのため、v=~~の部分を取り除くか、playlist?list=~~のようにurlを指定してください。) 

> **Warning**
> youtubeに上がっているものをダウンロードするのは規約違反なので自己責任.  
> 違法アップロードをしてあるものを知ってダウンロードするのは違法.  
> 公式が上げている(アーティスト本人など)ものをダウンロードするのは規約違反だが違法ではない.再配布はもちろん違法.  
> 以上のことを踏まえて使用すること.  

#### 更新
2023/4/5 ちゃんと動くようにしました ffmpegとyt-dlpのexeを入れています <br />
2023/4/17 ファイルからurlを読み込みダウンロード出来るようにしました. また、サムネイルも付けれるようになりました

#### 謝辞 <br />
https://github.com/soburi59/yt-dlp-music <br />
https://github.com/yt-dlp/yt-dlp <br />
https://github.com/FFmpeg/FFmpeg <br />
https://www.reddit.com/r/youtubedl/comments/rvj96t/comment/hut33u7