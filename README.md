# TKUHelper
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/image1.png" width="25%" height="25%"> <img src="https://github.com/yiweijiang/TKUHelper/blob/master/image2.jpeg" width="25%" height="25%">

A ChatBot help Tamkang University's students in the Line
### 研發動機：
雖然學校已經有一個APP「淡江I生活」，但在使用上仍然不是那麼方便，像是沒有辦法快速知道下堂課的資訊，或是查詢公車時限制很多等，於是我們想到使用Line這個即時通訊軟體，製作一個淡江學生專屬的Line bot ，可以在上課前主動提醒學生課程資訊，以及公車的即時查詢，並增加一些學生可能使用的功能。
### (一)、伺服器
**Heroku**是一個免費的PaaS(Platform as a Service)雲端服務，它能作為一個雲端平台讓使用者部署自己的程式，就像一個伺服器一樣，除此之外，Heroku也有提供SQL資料庫服務。在程式設計的時候，Heroku支持使用專門的Git伺服器進行代碼部署，這大大縮短了雲平台的學習時間。使用Heroku的好處是不用自己維護主機，不需要的時候也可以隨時停掉服務。透過Heroku，我們可以很輕鬆地將程式碼放到上面，達到架設伺服器的效果。
### (二)、程式
在前端使用者界面部分，利用Line所提供的API，我們可以根據不同的情景設定不同的操作方式，呈現給使用者不同視覺效果。
在後端部分，我們先在Line developers設定webhooks URL為放程式碼的Heroku網址，讓機器人可以接受到訊息，再根據接受到的訊息去逐步處理需要達到甚麼樣的動作、回覆，爬取資料我們使用requests，方法分為Get以及Post，中央氣象局、新北市政府公車動態資訊系統網站、蘋果新聞皆使用Get的方式獲取資料，而登入學校網頁爬取課程資料因為需要夾帶帳號密碼，所以使用Post方式把資料送出去，爬取完的資料都使用**Python**的Beautifulsoup模組處理，並擷取我們要的部分，資料庫是使用前面提到Heroku提供的**Postgresql**存放資料。
## 功能描述:
### (1)	登入
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/image3.png" width="25%" height="25%">  <br><br>
登入自己的帳號，需填寫學號、密碼、驗證碼。
### (2)	課程查詢
登入以後即可使用，可以查詢自己的所有課程，有課程名稱、授課教授、座號、上課時間、教室，也可以查詢今天的課。
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/image3.png" width="25%" height="25%">
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/image4.png" width="25%" height="25%">  <br><br>
### (3)	課程提醒
登入以後，將自動於上課前20分鐘提醒上課，提醒內容包含課程名稱、授課教授、座號、上課時間、教室，如不需要此功能也可以關閉。<br>
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/image5.jpeg" width="25%" height="25%">  <br><br>
### (4)	公車查詢
針對淡江學生經常搭乘的公車進行即時的查詢。<br>
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/image6.png" width="25%" height="25%">
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/image7.png" width="25%" height="25%">  <br><br>
### (5)	淡水天氣
針對淡水天氣進行查詢，內容包含溫度、體感溫度、濕度、降雨機率、天氣狀況、觀測地點、觀測時間。<br>
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/image8.jpeg" width="25%" height="25%">  <br><br>
### (6)	新聞
可收看近期最新的新聞，如果要看先前的新聞可以點選上一頁進行觀看。<br>
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/image10.png" width="25%" height="25%">
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/image11.jpeg" width="25%" height="25%">
<br><br>
### (7)	活動報名系統
即時查詢學校最近的活動。<br>
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/image3.png" width="25%" height="25%">  <br><br>
### (8)	記事本
學生可以把上課重點或是日常事情記錄下來，並可以記錄時間，並可以自行調整時間進行提醒。<br>
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/image12.png" width="25%" height="25%">
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/image13.png" width="25%" height="25%">

測試<br>
<img src="https://github.com/yiweijiang/TKUHelper/blob/master/TKU小幫手(QR).png" width="25%" height="25%">
