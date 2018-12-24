from flask import Flask, request, abort
from database.dbModel import *
from bs4 import BeautifulSoup
from imgurpython import ImgurClient
from Crypto.Cipher import DES
album_id = 'https://imgur.com/a/uYPDY'
import json
import os
import sys
import re
import time
import numpy as np
import requests
import urllib3
import io
import shutil
import PIL
from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib
import cv2
import pyimgur
import datetime
import gspread
from datetime import timedelta,timezone
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from oauth2client.service_account import ServiceAccountCredentials as SAC

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

################################################
@app.route("/news", methods=['GET'])
def news():
    '''get applenews_realtime'''
#    check_time = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
    try:
        applenews_crawler()
    except:
        print('Problem!')
    return 'OK'
############################
@app.route("/deleteCource", methods=['GET'])
def deleteCource():
    QUERY = db.session.query(Calendar).all()
    date = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
    nowdays = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M')    
    EXAM1 = datetime.datetime(QUERY[1].Year + 1911 ,int(QUERY[1].Month), int(QUERY[1].Day), 0, 0)    
    EXAM2 = datetime.datetime(QUERY[3].Year + 1911 ,int(QUERY[3].Month), int(QUERY[3].Day), 0, 0)    
    CHECK =  timedelta(days=0)
    Source_1 = datetime.datetime(QUERY[-2].Year + 1911 ,int(QUERY[-2].Month), int(QUERY[-2].Day), 0, 0) 
    Source_2 = datetime.datetime(QUERY[-1].Year + 1911 ,int(QUERY[-1].Month), int(QUERY[-1].Day), 0, 0) 
    if (EXAM1 - nowdays > CHECK and Source_1 - nowdays < CHECK) or (EXAM2 - nowdays > CHECK and Source_2 - nowdays < CHECK):
        print('NOYHING')
    else:
        delete = db.session.query(Elective_Data).all()
        for i in delete:
            db.session.delete(i)
            db.session.commit()            
        Delete = db.session.query(Cource).all()
        for j in Delete:
            db.session.delete(j)
            db.session.commit()   
    return 'OK'

###############################################
@app.route("/newsdelete", methods=['GET'])
def newsdelete():

    news = db.session.query(Apple_Realtime_News).all()
    len_news = len(news)
    if len_news > 300:

        news_id = db.session.query(Apple_Realtime_News.id).all()
        sort_news = sorted(news_id)

        for x in sort_news[:100]:
            delete = db.session.query(Apple_Realtime_News).filter(Apple_Realtime_News.id==x).first()
            db.session.delete(delete)
            db.session.commit()
    return 'OK'

################################################
@app.route("/weather", methods=['GET'])
def weather():
    '''update the weather data'''
    GetWeather()
    return 'OK'


@app.route("/calendar", methods=['GET'])
def calendar():
    '''update the Calendar data'''
    GetCalendar()
    return 'OK'

@app.route("/TechNews", methods=['GET'])
def TechNews():
    soup = connect('https://technews.tw/')
    tds = soup.find_all("td","maintitle")[::-1]
    POST = soup.find_all('article',id=='post')[::1]
    for t in range(0,len(tds)):
        if tds[t].find('a'):
            href = tds[t].find('a')['href']
            CHECK_QUERY = db.session.query(Tech_News).filter(Tech_News.URL == href).first()
            if CHECK_QUERY == None:
                title = tds[t].find('a').string
                image_url = POST[t].find('img')['src']
                insert_data = Tech_News(
                    TITLE = title,
                    URL = href,
                    IMAGE_URL = image_url
                )
                db.session.add(insert_data)
                db.session.commit()
            else:
                continue
    return 'OK'
################################################

@app.route("/RemindNote", methods=['GET'])
def RemindNote():
    date = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
    nowdays = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M')
    AllUser = db.session.query(USER_DATA.LINE_ID).all()
    for user in AllUser:
        alldata = db.session.query(Notebook).filter(Notebook.USER_ID == user[0]).all()
        if alldata == None:
            continue
        for x in alldata:
            if x.RemindTime != None:
                if x.WhenRemind != None:
                    compare = x.RemindTime - nowdays
                    remind = re.split('-',x.WhenRemind)
                    if len(remind) != 3:
                        continue
                    day, hour, minute = int(remind[0]), int(remind[1]), int(remind[2])
                    Remind =  timedelta(days=day,hours=hour,minutes=minute)
                    source = Remind - timedelta(minutes=5)
                    destination = Remind + timedelta(minutes=5)
                    if source < compare < destination:
                        title, time, Description = x.Event, x.Time, x.Description
                        buttons_template_message = TemplateSendMessage(
                        alt_text='Buttons template',
                            template=ButtonsTemplate(
                                thumbnail_image_url = 'https://imgur.com/od2Qlu5.png',
                                title=title,
                                text=time + '\n' + Description,
                                actions = [
                                    PostbackTemplateAction(
                                        label='更改',
                                        text = '更改:' + title,    
                                        data = 'change###'+title+'###'+time+'###'+Description
                                    ),
                                    PostbackTemplateAction(
                                        label = '刪除',
                                        data = '刪除###'+title+'###'+time+'###'+Description
                                    )
                                ]
                            )    
                        )
                        line_bot_api.push_message(user[0],buttons_template_message)
                else:
                    continue
            else:
                continue
        else:
            continue
    return 'OK'


@app.route("/remind/BeforeClass", methods=['GET'])
def remind():
    '''remind everyone where they should go to the class'''
    date = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%H:%M')
    check_time = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%w')
    week = ''
    if check_time == '0':
        week = '日'
    elif check_time == '1':
        week = '一'
    elif check_time == '2':
        week = '二'
    elif check_time == '3':
        week = '三'
    elif check_time == '4':
        week = '四'
    elif check_time == '5':
        week = '五'
    else:
        week = '六'
    date_array = re.split(':',date)
    hour = int(date_array[0])
    minute = int(date_array[1])
    nowdays = timedelta(hours=hour,minutes=minute)
    remind_format = timedelta(hours=0,minutes=20)
    source =  timedelta(hours=0,minutes=10)
    CHECK_QUERY = db.session.query(USER_DATA).all()
    for user_data in CHECK_QUERY:
        reply=''
        Line_ID = user_data.LINE_ID
        Student_ID = str(user_data.Student_ID)
        if user_data.Student_ID  == 0 or user_data.Remind == False:
            continue
        CHECK_Cource = db.session.query(Elective_Data.Cource,Elective_Data.Number).filter(Elective_Data.Student_ID==Student_ID).all()
        if CHECK_Cource == None:
            continue
        for cource in CHECK_Cource:
            QUERY_Cource = db.session.query(Cource).filter(Cource.Number==cource[0]).all()
            for DATA in QUERY_Cource:
                Week = DATA.Week
                if Week == None:
                    continue
                if re.search(week,Week):
                    Cource_Time = DATA.Time
                    SEARCH = re.split('（',Cource_Time)[-1][:5]
                    show = re.split(':',SEARCH)
                    hours = int(show[0])
                    minutes = int(show[1])
                    remind_time = timedelta(hours=hours,minutes=minutes)-nowdays                    
                    if source <= remind_time <= remind_format:
                        Cource_Teacher = DATA.Teacher        
                        Cource_Name = DATA.Name
                        Number = ''
                        if cource[1] != 0:
                            Number = str(cource[1])+'號'
                        else:
                            Number = ''
                        reply = Cource_Name + '\n'+Cource_Teacher+ '\u3000' + Number +'\n' + Cource_Time
                        REPLY = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == Line_ID).first().LastCource
                        if reply != REPLY:
                            line_bot_api.push_message(Line_ID,TextSendMessage(text=reply))
                            data = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == Line_ID).update({'LastCource':reply})
                            db.session.commit()
                        else:
                            continue
                    else:
                        continue
                else:
                    continue
    return 'OK'

################################################

@handler.add(FollowEvent)
def handle_message(event):
    delete = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id).all()

    for data in delete:
        db.session.delete(data)
        db.session.commit()
    insert_data = USER_DATA(LINE_ID = event.source.user_id,
                          Add_Event = '', 
                          Add_Time = '', 
                          Add_Index = 0, 
                          Change_Event = '',     
                          Change_Type = '',
                          Change_Index = 0,
                          Delete_Event = '',
                          Curriculum_Cookie = '',
                          Status = 0,
                          Student_ID = 0,  
                          Remind = True,  
                          encrypt = None,
                          LastCource = None
                      )  
    print("OK")
    db.session.add(insert_data)
    db.session.commit()

###########################
@handler.add(UnfollowEvent)
def handle_message(event):
    delete = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id).all()

    for data in delete:
        db.session.delete(data)
        db.session.commit()

    query = db.session.query(USER_DATA.LINE_ID).all()


################################################
@handler.add(JoinEvent)
def handle_message(event):
    print(event)
    insert_data = USER_DATA(LINE_ID = event.source.group_id,
                          Add_Event = '', 
                          Add_Time = '', 
                          Add_Index = 0, 
                          Change_Event = '',     
                          Change_Type = '',
                          Change_Index = 0,
                          Delete_Event = '',
                          Curriculum_Cookie = '',
                          Status = 0,
                          Student_ID = 0,  
                          Remind = True, 
                          encrypt = None,
                          LastCource = None
                      )    
    print("OK")
    db.session.add(insert_data)
    db.session.commit()

################################################

@handler.add(LeaveEvent)
def handle_message(event):

    delete = db.session.query(Data).filter(Data.name == event.source.group_id).all()

    if delete == None :
        print('OK')
    else :
        for data in delete:
            db.session.delete(data)
            db.session.commit()

    delete_check = db.session.query(CHECK).filter(CHECK.user_id == event.source.group_id).all()
    if delete_check == None :
        print('OK')
    else :
        for data in delete_check:
            db.session.delete(data)
            db.session.commit()

################################################

@handler.add(PostbackEvent)
def handle_message(event):
    data = event.postback.data
    if data == '&mode=datetime':
        check = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id).first().Status
        if check == 1:
            time = event.postback.params['datetime']
            search = re.split('T',time)
            time = ' '.join(search)
            add_time = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id).update({'Add_Index':1,'Add_Time':time})
            text = '描述一下你的事情吧~'
            line_bot_api.reply_message(event.reply_token,TextMessage(text='你輸入:'+time))
            line_bot_api.push_message(event.source.user_id,TextSendMessage(text))
            db.session.commit()
        else:
            text = '你已經取消，請重新輸入'
            line_bot_api.push_message(event.source.user_id,TextSendMessage(text))

    elif data == '取消':
        add_time = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id).update({'Status':0,'Add_Index':0,'Change_Index':0,'Status':0})
        db.session.commit()
        line_bot_api.reply_message(event.reply_token,TextMessage(text='你已經取消'))

    elif data == '開啟提醒':
        update = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id).update({'Remind':True})
        db.session.commit()
        line_bot_api.reply_message(event.reply_token,TextMessage(text='你已經開啟提醒服務'))

    elif data == '關閉提醒':
        update = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id).update({'Remind':False})
        db.session.commit()
        line_bot_api.reply_message(event.reply_token,TextMessage(text='你已經關閉提醒服務'))

    elif data == '不輸入時間':
        check = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id).first().Status
        if check == 1:
            add_time = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id).update({'Add_Index':1,'Add_Time':' '})
            text = '描述一下你的事情吧~'

            line_bot_api.push_message(event.source.user_id,TextSendMessage(text))
            db.session.commit()
        elif check == 2:
            data = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id)


            ID = data.first().Change_Event

            s = db.session.query(Notebook).filter(Notebook.id==ID).update({'Time':' ','RemindTime':None})

            add_time = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id).update({'Add_Index':0,'Add_Time':' ','Status':0})
            #data = db.session.query(Notebook).filter(Notebook.USER_ID == event.source.user_id).update({'RemindTime':None})
            db.session.commit()
            text = '已經修改好囉'
            line_bot_api.push_message(event.source.user_id,TextSendMessage(text))
        else:
            text = '你已經取消，請重新輸入'
            line_bot_api.push_message(event.source.user_id,TextSendMessage(text))

    elif re.match('change###', data):
        search = re.split('###',data)
        check = db.session.query(Notebook.id).filter(Notebook.USER_ID == event.source.user_id).filter(Notebook.Event==search[1]).filter(Notebook.Time==search[2]).filter(Notebook.Description==search[3]).first()
        print(check)

        if check != None:
            CHECK = check[0]
            data = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id).update({'Change_Event':CHECK}) 
            db.session.commit()

    elif data == '&mode=change':
        time = event.postback.params['datetime']
        search = re.split('T',time)
        time = ' '.join(search)
        data = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id)
        ID = data.first().Change_Event
        newdata = data.update({'Status':0})
        s = db.session.query(Notebook).filter(Notebook.id==ID)
        if s.first() != None:
            s.update({'Time':time,'RemindTime':time})
            db.session.commit()
            line_bot_api.reply_message(event.reply_token,TextMessage(text='OK'))

    elif data == '登出':
        set_data = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id)
        CHECK = str(set_data.first().Student_ID)
        QUERY_Exist = db.session.query(Elective_Data.Cource).filter(Elective_Data.Student_ID==CHECK).first()
        if CHECK == 0 or QUERY_Exist==None:

            line_bot_api.reply_message(event.reply_token,TextMessage(text='你還沒登入喔~'))

        else:
            data = set_data.update({'Status':0,'Student_ID':0,'Add_Index':0,'encrypt':None})
            db.session.commit()

            line_bot_api.reply_message(event.reply_token,TextMessage(text='已經登出囉~'))

    elif re.search('刪除###',data):
        search = re.split('###',data)
        check = db.session.query(Notebook.id).filter(Notebook.USER_ID == event.source.user_id).filter(Notebook.Event==search[1]).filter(Notebook.Time==search[2]).filter(Notebook.Description==search[3]).first()
        if check !=None:
            data = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id).update({'Delete_Event':check[0]}) 
            text = '你確定要刪除它嗎？'
            db.session.commit()
            confirm_template_message = confirm_template(text,'幫我刪除它','#delete','算了吧','#no')
            line_bot_api.reply_message(event.reply_token,confirm_template_message)
        else:
            line_bot_api.reply_message(event.reply_token,TextMessage(text='你已經刪除囉！'))


    elif re.match('更多記事 ',data):
        alldata = db.session.query(Notebook).filter(Notebook.USER_ID == event.source.user_id).all()
        last_number = re.split(' ',data)[-1]

        event_number = []
        car = []
        DATA = []   

        last_len = int(last_number)
        new_len = last_len - 9
        print(last_len)
        print(new_len)

        for data in alldata:
            title = data.Event
            see_time = data.Time
            description = data.Description    
            event_number.append(title)    
            event_number.append(see_time)
            event_number.append(description)
            car.append(event_number)
            event_number = []
        if last_len > len(alldata):
            carousel = CarouselColumn(
                    thumbnail_image_url = 'https://imgur.com/ya0Vj4y.jpg',
                    title = '更多記事',
                    text =  '請選擇',
                    actions = [
                        PostbackTemplateAction(
                            label=' ',
                            data = ' '
                        ),
                        PostbackTemplateAction(
                            label='下一頁',
                            data = '更多記事 '+str(len(alldata)-9)
                        )
                    ]
                 )
            DATA.append(carousel)
            for i in range(-10,-1):
                title = car[i][0]           
                A = CarouselColumn(
                        thumbnail_image_url = 'https://imgur.com/od2Qlu5.png',
                        title = title,
                        text =  car[i][1] + '\n'+car[i][2],
                        actions = [
                            PostbackTemplateAction(
                                label='更改',
                                text = '更改:' + car[i][0],
                                data = 'change###'+car[i][0]+'###'+car[i][1]+'###'+car[i][2]
                            ),
                            PostbackTemplateAction(
                               label = '刪除',
                               data = '刪除###'+car[i][0]+'###'+car[i][1]+'###'+car[i][2]
                            )
                        ]
                     )
                DATA.append(A)
        elif last_len > 9:
            carousel = CarouselColumn(
                thumbnail_image_url = 'https://imgur.com/ya0Vj4y.jpg',
                    title = '更多記事',
                    text =  '請選擇',
                    actions = [
                        PostbackTemplateAction(
                            label='上一頁',
                            data = '更多記事 ' + str(last_len+18)
                        ),
                        PostbackTemplateAction(
                            label='下一頁',
                            data = '更多記事 ' + str(new_len-9)
                        )
                    ]
                 )
            DATA.append(carousel)
            for i in range(last_len-10,last_len-1):
                title = car[i][0]           
                A = CarouselColumn(
                        thumbnail_image_url = 'https://imgur.com/od2Qlu5.png',
                        title = title,
                        text =  car[i][1] + '\n'+car[i][2],
                        actions = [
                            PostbackTemplateAction(
                                label='更改',
                                text = '更改:' + car[i][0],
                                data = 'change###'+car[i][0]+'###'+car[i][1]+'###'+car[i][2]
                            ),
                            PostbackTemplateAction(
                               label = '刪除',
                               data = '刪除###'+car[i][0]+'###'+car[i][1]+'###'+car[i][2]
                            )
                        ]
                     )
                DATA.append(A)

        else:
            carousel = CarouselColumn(
                thumbnail_image_url = 'https://imgur.com/ya0Vj4y.jpg',
                    title = '更多記事',
                    text =  '請選擇',
                    actions = [
                        PostbackTemplateAction(
                            label=' ',
                            data = ' '
                        ),
                        PostbackTemplateAction(
                            label='上一頁',
                            data = '更多記事 ' + str(last_len+18)
                        )
                    ]
                 )
            DATA.append(carousel)
            for i in range(0, last_len+8):
                title = car[i][0]           
                A = CarouselColumn(
                    thumbnail_image_url = 'https://imgur.com/od2Qlu5.png',
                        title = title,
                        text =  car[i][1] + '\n'+car[i][2],
                        actions = [
                            PostbackTemplateAction(
                                label='更改',
                                text = '更改:' + car[i][0],
                                data = 'change###'+car[i][0]+'###'+car[i][1]+'###'+car[i][2]
                            ),
                            PostbackTemplateAction(
                               label = '刪除',
                               data = '刪除###'+car[i][0]+'###'+car[i][1]+'###'+car[i][2]
                            )
                        ]
                     )
                DATA.append(A)

        carousel_template_message = TemplateSendMessage(
                alt_text = 'Carousel template',
                template = CarouselTemplate(DATA)
            )
        line_bot_api.reply_message(event.reply_token,carousel_template_message)

    elif data == '#no':
        sticker_message = StickerSendMessage(
                package_id='2',
                sticker_id='144'
            )
        line_bot_api.reply_message(event.reply_token,sticker_message)


    elif re.match('蘋果新聞 ',data):
        number = int(re.split(' ',data)[1])
        news_range = 0
        DATA = []
        reply_data=''
        CHECK_QUERY = db.session.query(Apple_Realtime_News).all()
        if 0 <= number <= len(CHECK_QUERY):
            news_range = number
            carousel = CarouselColumn(
                    thumbnail_image_url = 'https://imgur.com/ya0Vj4y.jpg',
                    title = '更多新聞',
                    text =  '請選擇',
                    actions = [
                        PostbackTemplateAction(
                            label='上一頁',
                            data = '蘋果新聞 '+str(news_range-9)
                        ),
                        PostbackTemplateAction(
                            label='下一頁',
                            data = '蘋果新聞 '+str(news_range+9)
                        )
                    ]
                 )
            DATA.append(carousel)


            news_id = db.session.query(Apple_Realtime_News.id).all()
            sort_news = sorted(news_id)
            for x in sort_news[news_range-9:news_range]:
                QUERY = db.session.query(Apple_Realtime_News).filter(Apple_Realtime_News.id==x).first()
                time = QUERY.DATE
                title = QUERY.TITLE
                href = QUERY.URL
                image_url = QUERY.IMAGE_URL
                news_type = QUERY.NEWS_Type
                reply_data = reply_data + title + '\n' + href + '\n'
                A = CarouselColumn(
                    thumbnail_image_url = image_url,
                    title = title,
                    text =  news_type,
                    actions = [
                        URITemplateAction(
                           label = '瀏覽網頁',
                           uri = href
                        ),
                        PostbackTemplateAction(
                            label=' ',
                            data = ' '
                        )
                    ]
                 )
                DATA.append(A)

            carousel_template_message = TemplateSendMessage(
                alt_text = 'Carousel template',
                template = CarouselTemplate(DATA)
            )
            line_bot_api.reply_message(event.reply_token,carousel_template_message)
        elif number < 0:        
            line_bot_api.reply_message(event.reply_token,TextMessage(text='你已經看完囉'))           
        else:
            line_bot_api.reply_message(event.reply_token,TextMessage(text='這已經是最新的新聞'))            
    else:
        print(data)

###################################################################

@handler.add(MessageEvent, message=StickerMessage)
def handle_message(event):
    print(event)

###################################################################

@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)

#    with open('test','wb') as fd:
#        for chunk in message_content.iter_content():
#            fd.write(chunk)
 

###################################################################

@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    print(event.message.address)
    #line_bot_api.reply_message(event.reply_token,TextMessage(text=event.message.address))

###################################################################

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    user_type = event.source.type
    print(user_type)

    user_text = event.message.text

    CHECK_QUERY = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id)

    set_data = CHECK_QUERY.first()

    Status = 0
    Add_Index = 0
    Change_Index = 0

    if set_data==None :
        insert_data = USER_DATA(LINE_ID = event.source.user_id,
                          Add_Event = '', 
                          Add_Time = '', 
                          Add_Index = 0, 
                          Change_Event = '',     
                          Change_Type = '',
                          Change_Index = 0,
                          Delete_Event = '',
                          Curriculum_Cookie = '',
                          Status = 0,
                          Student_ID = 0, 
                          Remind = True,   
                          encrypt = None,
                          LastCource = None
                      )
        db.session.add(insert_data)
        db.session.commit()
    else :
        Status = set_data.Status
        Add_Index = set_data.Add_Index
        Change_Index = set_data.Change_Index


    if Status == 1:
        if Add_Index == 0:
            initial = datetime.datetime.now().strftime('%Y-%m-%dT00:00')
            data = CHECK_QUERY.update({'Add_Event':user_text})
            time_message = TemplateSendMessage(
                alt_text='Buttons template',
                template = ButtonsTemplate(
                    thumbnail_image_url = 'https://imgur.com/sSueFLd.jpg',
                    title = '輸入你的時間',
                    text = 'Please select',    
                    actions = [
                        DatetimePickerTemplateAction(
                            label = '日期還有時間',
                            mode = 'datetime',
                            data = '&mode=datetime',
                            initial = initial,
                            min = initial,    
                            max = '2040-12-31T23:59'
                        ),
                        PostbackTemplateAction(
                           label = '不輸入時間',
                           data = '不輸入時間'
                        ),
                        PostbackTemplateAction(
                           label = '取消',
                           data = '取消'
                        )
                    ]
                )
            )
            line_bot_api.push_message(event.source.user_id,TextSendMessage(text='你輸入:'+ user_text))
            line_bot_api.reply_message(event.reply_token,time_message)
            db.session.commit()

        elif Add_Index == 1:
 
            time = set_data.Add_Time
            if time == ' ':
                time = None

            insert_data = Notebook( USER_ID = event.source.user_id
                          , Event = set_data.Add_Event
                          , Time = set_data.Add_Time
                          , Description = user_text
                          , RemindTime = time
                          , WhenRemind = '00-00-30'
                          )
            db.session.add(insert_data)
            data = CHECK_QUERY.update({'Status':0,'Add_Index':0})
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='已經幫你記起來囉'))
            db.session.commit()

##################

    elif re.search('#change', user_text):
        change_data = set_data.Change_Event
        alldata = db.session.query(Notebook).filter(Notebook.id == change_data).first()
        if alldata == None:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='找不到這件事情，你可能已經刪除囉~'))
        else :
            data = CHECK_QUERY.update({'Status':2})
            db.session.commit()
            Event = alldata.Event
            Time = alldata.Time
            Description = alldata.Description

            REMIND = '不提醒'

            if alldata.WhenRemind != None:
                Remind = re.split('-',alldata.WhenRemind)
                day, hour, minute = Remind[0], Remind[1], Remind[2]
                if int(day) == 0:
                    day = ''
                else:
                    day = day + '天'
                if int(hour) == 0:
                    hour = ''
                else:
                    hour = hour + '小時'
                if int(minute) == 0:
                    minute = ''
                else:
                    minute = minute + '分'
                REMIND = day + hour + minute + '前提醒'

            if Time.isspace():
                Time = '未輸入時間'
            buttons_template_message = TemplateSendMessage(
                alt_text = 'Buttons template',
                template=ButtonsTemplate(
                    thumbnail_image_url = 'https://imgur.com/od2Qlu5.png',
                    title = '你想更改什麼？',
                    text = '請選擇',    
                    actions = [
                        MessageTemplateAction(
                            label = Event,
                            text = '#event'
                        ),
                        MessageTemplateAction(
                            label = Time,
                            text = '#time'
                        ),
                        MessageTemplateAction(
                            label = Description,
                            text = '#content'
                        ),
                        MessageTemplateAction(
                            label = REMIND,
                            text = '#remind'
                        )
                    ]
                )    
            )
            line_bot_api.reply_message(event.reply_token,buttons_template_message)

##################

    elif Status == 2:
        if Change_Index == 0:
            if user_text == '#event':
                text = 'Event'
                user_text = '事情'
                data = CHECK_QUERY.update({'Change_Index':1,'Change_Type':text})
                db.session.commit()
                text = "輸入新的" + user_text
                line_bot_api.reply_message (event.reply_token,TextSendMessage(text))

            elif user_text == '#remind':
                text = 'WhenRemind'
                user_text = '提醒時間\n格式：天-小時-分鐘\nex：0-5-15\n(表示5小時15分前提醒)'
                data = CHECK_QUERY.update({'Change_Index':1,'Change_Type':text})
                db.session.commit()
                text = "輸入新的" + user_text
                line_bot_api.reply_message (event.reply_token,TextSendMessage(text))


            elif user_text == '#content':
                text = 'Description'
                user_text = '內容'
                data = CHECK_QUERY.update({'Change_Index':1,'Change_Type':text})
                db.session.commit()
                text = "輸入新的" + user_text
                line_bot_api.reply_message (event.reply_token,TextSendMessage(text))

            elif user_text == '#time':
                print(datetime.datetime.now())
                text='Time'
                initial = datetime.datetime.now().strftime('%Y-%m-%dT00:00')
                time_message = TemplateSendMessage(
                    alt_text='Buttons template',
                    template = ButtonsTemplate(
                        thumbnail_image_url = 'https://imgur.com/od2Qlu5.png',
                        title = '輸入新的時間',
                        text = 'Please select',    
                        actions = [
                        DatetimePickerTemplateAction(
                            label = '日期還有時間',
                            mode = 'datetime',
                            data = '&mode=change',
                            initial = initial,
                            min = initial,    
                            max = '2040-12-31T23:59'
                        ),
                        PostbackTemplateAction(
                           label = '不輸入時間',
                           data = '不輸入時間'
                        ),
                        PostbackTemplateAction(
                           label = '取消',
                           data = '取消'
                        )
                        ]
                    )
                )
                data = CHECK_QUERY.update({'Change_Index':1,'Change_Type':text})
                db.session.commit()
                line_bot_api.reply_message (event.reply_token,time_message)

            else:
                text = "請重新更改，並使用上方按鈕!"
                data = CHECK_QUERY.update({'Status':0})
                db.session.commit()
                line_bot_api.reply_message (event.reply_token,TextSendMessage(text=text))

        elif Change_Index == 1:
            data = CHECK_QUERY.first()

            change_data = data.Change_Event
            change_type = data.Change_Type

            if change_type == 'WhenRemind':
                Time = re.split('-',user_text)
                if len(Time) == 3 and Time[0].isdigit() and Time[1].isdigit() and Time[2].isdigit() and int(Time[1]) < 24 and int(Time[2]) < 60:
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='更改完成'))
                    data1 = db.session.query(Notebook).filter(Notebook.id == change_data).update({change_type:user_text})
                    db.session.commit()
                else:
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='不符合格式，請重新更改'))
            else:
                data1 = db.session.query(Notebook).filter(Notebook.id == change_data).update({change_type:user_text})
                db.session.commit()
                line_bot_api.reply_message (event.reply_token,TextSendMessage(text='更改完成'))
            data = CHECK_QUERY.update({'Change_Index':0,'Status':0})
            db.session.commit()

        else:
            text = "更改錯誤，請重新嘗試"
            data = CHECK_QUERY.update({'Change_Index':0,'Status':0})

            db.session.commit()        
            line_bot_api.reply_message (event.reply_token,TextSendMessage(text))

##################

    elif Status == 3:
        key = 'tkujiang'
        obj = DES.new(key,DES.MODE_ECB)
        lengh = len(user_text)
        add = 8 - (lengh%8)
        text = ''
        if Add_Index == 1:

            Student_ID = user_text

            if Student_ID.isdigit() and len(Student_ID) >= 9:
                Student_ID = user_text
                data = CHECK_QUERY.update({'Add_Index':2,'Student_ID':Student_ID})

                line_bot_api.reply_message (event.reply_token,TextSendMessage(text='請輸入你的密碼~'))

                #line_bot_api.push_message(event.source.user_id,TextSendMessage(text='請輸入你的密碼~'))
            else:
                line_bot_api.reply_message (event.reply_token,TextSendMessage(text='學號輸入錯誤!'))            
                data = CHECK_QUERY.update({'Status':0,'Add_Index':0,'Student_ID':0})

            db.session.commit()

        elif Add_Index == 2:

            requests.packages.urllib3.disable_warnings()
            rs = requests.session()
            res = rs.get('https://sso.tku.edu.tw/NEAI/ImageValidate', stream = True)
            cookie = rs.cookies.get_dict()['AMWEBJCT!%2FNEAI!JSESSIONID']
            f = open('check.png','wb')
            shutil.copyfileobj(res.raw,f)
            f.close()

            PATH = "check.png"
            im = pyimgur.Imgur(client_id)
            uploaded_image = im.upload_image(PATH, title="test")

            image = ImageSendMessage(
                    original_content_url=uploaded_image.link,
                    preview_image_url=uploaded_image.link
                )

            try:
                text=''
                for x in range(0,add):
                    text = text + 'X'
                encrypt = obj.encrypt(user_text+text)
                data = CHECK_QUERY.update({'Curriculum_Cookie':cookie,'Add_Index':3,'encrypt':encrypt})
                db.session.commit()
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text='請輸入驗證碼'))

                line_bot_api.reply_message (event.reply_token,image)

                #line_bot_api.push_message(event.source.user_id,image)       
            except:

                line_bot_api.reply_message (event.reply_token,TextSendMessage(text='密碼格式有誤，請重新登入'))

                #line_bot_api.push_message(event.source.user_id,TextSendMessage(text='密碼格式有誤，請重新登入'))
                data = CHECK_QUERY.update({'Status':0,'Student_ID':0,'Add_Index':0,'encrypt':None})
                db.session.commit()

        elif Add_Index == 3:

            Student_ID = set_data.Student_ID
            PWD = ''
            key = 'tkujiang'
            obj = DES.new(key,DES.MODE_ECB)

            try:
                decrypt = obj.decrypt(set_data.encrypt)
                decrypt_str = bytes.decode(decrypt)
                PWD = re.split('X',decrypt_str)[0]
            except:
                data = CHECK_QUERY.update({'Status':0,'Student_ID':0,'Add_Index':0})
                db.session.commit() 

            pay = {
                'myurl':'http://sso.tku.edu.tw/aissinfo/emis/tmw0012.aspx',
                'ln':'zh_TW',
                'embed':'No',
                'logintype':'logineb',
                'username':Student_ID,
                'password':PWD,
                'vidcode':user_text,
                'loginbtn':'登入'
            }
        
            cookie = CHECK_QUERY.first().Curriculum_Cookie
            cookies = {
                'AMWEBJCT!%2FNEAI!JSESSIONID':cookie
                }
            try:
                
                QUERY = db.session.query(Calendar).all()
              
                
                date = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
                nowdays = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M')    
                s = QUERY[0].Year + 1912
                EXAM =datetime.datetime(s ,int(QUERY[1].Month), int(QUERY[1].Day), 0, 0)         
                num = str(QUERY[0].Year)
                
                CHECK =  timedelta(days=0)
                
                
                if EXAM - nowdays > CHECK:
                    num = num + '1'
                else:
                    num = num + '2'                
                
                rs = requests.session()
                res = rs.post('https://sso.tku.edu.tw/NEAI/login2.do?action=EAI',data=pay,cookies=cookies,verify = False)
                res2 = rs.get('http://sso.tku.edu.tw/aissinfo/emis/TMWC020_result.aspx?YrSem='+num+'&stu_no='+str(Student_ID),verify = False)
                res3 = rs.get('http://sso.tku.edu.tw/aissinfo/emis/TMWC020_result.aspx?YrSem='+num+'&stu_no='+str(Student_ID),verify = False)

            except Exception as ex:
                print('PROBLEM!!')

            CHECK = str(set_data.Student_ID)

            Delete_Cource = db.session.query(Elective_Data).filter(Elective_Data.Student_ID==CHECK).all()
            if Delete_Cource != None:
                for delete in Delete_Cource:
                    db.session.delete(delete)
                    db.session.commit()
            try:
                cource_array=[]
                cource=[]
                soup = BeautifulSoup(res3.text, 'html.parser')
                
                data = soup.find_all('table')[1].find_all('tr')
                
                for tr in data:
                    for table in tr:
                        try:
                            cource.append(table.text)
                        except Exception as ex:
                            continue
                    cource_array.append(cource)
                    cource = []
                    
                print('THIS')
                    
                for cource in cource_array:
                    if cource[0].isdigit():
                        if cource[12].isdigit():
                            Number = cource[12]
                        else:
                            Number = 0

                        insert_data = Elective_Data(
                            Student_ID = Student_ID,
                            Cource = cource[0],
                            Number = Number         
                        )
                        db.session.add(insert_data)
                        db.session.commit()
                    else:
                        print(' ')
                data = CHECK_QUERY.update({'Status':0,'Add_Index':0})
                db.session.commit()
                QUERY_Cource = db.session.query(Elective_Data.Cource).filter(Elective_Data.Student_ID==CHECK).all()
                ID = set_data.Student_ID
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text='登入成功,請稍等'))
                reply = ''
                MON=''
                TUE=''
                WED=''
                THU=''
                FRI=''
                SAT=''
                SUN=''
                try:
                    for cource in QUERY_Cource:
                        check = db.session.query(Cource).filter(Cource.Number==cource[0]).first()
                        if check == None:
                            Get_Cource(cource[0])

                        else:
                            continue
                    line_bot_api.push_message(event.source.user_id,TextSendMessage(text='已成功登入！'))
                except Exception as ex:
                    line_bot_api.push_message(event.source.user_id,TextSendMessage(text='載入資料有問題，請登出後再嘗試登入\n如無法登入，請聯絡開發人員'))
                    data = CHECK_QUERY.update({'Status':0,'Student_ID':0,'Add_Index':0,'encrypt':None})
                    db.session.commit()
            except Exception as ex:
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text='帳號或密碼輸入錯誤!'))
                data = CHECK_QUERY.update({'Status':0,'Student_ID':0,'Add_Index':0,'encrypt':None})
                db.session.commit()

##################

    elif user_text == '登出':
        confirm_template_message = TemplateSendMessage(
            alt_text='Confirm template',
                template=ConfirmTemplate(
                text= '確定要登出嗎？',
                actions = [
                    PostbackTemplateAction(
                        label='登出',
                        data='登出'
                    ),
                    PostbackTemplateAction(    
                        label='不用了',
                        data='#no'
                    )
                ]
            )
        )

        CHECK = str(set_data.Student_ID)
        QUERY_Exist = db.session.query(Elective_Data.Cource).filter(Elective_Data.Student_ID==CHECK).first()
        if CHECK == 0 or QUERY_Exist==None:
            line_bot_api.push_message(event.source.user_id,TextSendMessage(text='你還沒登入喔~'))
        else:

            line_bot_api.reply_message(event.reply_token,confirm_template_message)

##################

    elif user_text == '記事本':
        buttons_template_message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                thumbnail_image_url='https://imgur.com/od2Qlu5.jpg',
                title='我能幫你嗎??',
                text='說說你的故事吧',
                actions = [
                    MessageTemplateAction(
                        label='我有什麼事',
                        text='#see'
                    ),
                    MessageTemplateAction(
                        label='幫我記事情',
                        text='#add'
                    )
                ]
            )    
        )
        line_bot_api.reply_message(
            event.reply_token,
            buttons_template_message)

        data = CHECK_QUERY.update({'Status':0,'Add_Index':0,'Status':0,'Change_Index':0})
        db.session.commit()



##################

    elif user_text == '#add':
        data = CHECK_QUERY.update({'Status':1})
        db.session.commit()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = '沒問題!請問有什麼事?'))
      
##################  
        
    elif re.match('更改', user_text):

        alldata = db.session.query(USER_DATA).filter(USER_DATA.LINE_ID == event.source.user_id).first()
        if alldata != None:

            alldata = alldata.Change_Event 
            change = '更改:' + alldata
            if change == '更改:':
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="它不存在~"))
            else :
                text = '你確定要更改?'
                confirm_template_message = confirm_template(text,'我想更改它','#change','不用了','#no')
                line_bot_api.reply_message(event.reply_token,confirm_template_message)



##################

    elif user_text == '#see' :
        alldata = db.session.query(Notebook).filter(Notebook.USER_ID == event.source.user_id).all()
        data_len = len(alldata)
        print(data_len)
        if alldata == [] :    
            line_bot_api.reply_message(event.reply_token,TextSendMessage('你還沒記任何事喔'))
        else:
            event_number = []
            car = []
            DATA = []   
            for data in alldata:
                title = data.Event
                see_time = data.Time
                description = data.Description    
                event_number.append(title)    
                event_number.append(see_time)
                event_number.append(description)
                car.append(event_number)
                event_number = []
            if data_len > 9:
                carousel = CarouselColumn(
                    thumbnail_image_url = 'https://imgur.com/ya0Vj4y.jpg',
                    title = '更多記事',
                    text =  '請選擇',
                    actions = [
                        PostbackTemplateAction(
                            label=' ',
                            data = ' '
                        ),
                        PostbackTemplateAction(
                            label='下一頁',
                            data = '更多記事 '+str(data_len-9)
                        )
                    ]
                 )
                DATA.append(carousel)
                for i in range(-10,-1):
                    title = car[i][0]           
                    A = CarouselColumn(
                        thumbnail_image_url = 'https://imgur.com/od2Qlu5.png',
                        title = title,
                        text =  car[i][1] + '\n'+car[i][2],
                        actions = [
                            PostbackTemplateAction(
                                label='更改',
                                text = '更改:' + car[i][0],
                                data = 'change###'+car[i][0]+'###'+car[i][1]+'###'+car[i][2]
                            ),
                            PostbackTemplateAction(
                               label = '刪除',
                               data = '刪除###'+car[i][0]+'###'+car[i][1]+'###'+car[i][2]
                            )
                        ]
                     )
                    DATA.append(A)

            else:
                for i in range(0, len(car)):
                    title = car[i][0]           
                    A = CarouselColumn(
                        thumbnail_image_url = 'https://imgur.com/od2Qlu5.png',
                        title = title,
                        text =  car[i][1] + '\n'+car[i][2],
                        actions = [
                            PostbackTemplateAction(
                                label='更改',
                                text = '更改:' + car[i][0],
                                data = 'change###'+car[i][0]+'###'+car[i][1]+'###'+car[i][2]
                            ),
                            PostbackTemplateAction(
                               label = '刪除',
                               data = '刪除###'+car[i][0]+'###'+car[i][1]+'###'+car[i][2]
                            )
                        ]
                     )
                    DATA.append(A)


            carousel_template_message = TemplateSendMessage(
                alt_text = 'Carousel template',
                template = CarouselTemplate(DATA)
            )
            line_bot_api.reply_message(event.reply_token,carousel_template_message)

###################
    elif user_text == '蘋果新聞': 
        DATA = []
        reply_data=''
        CHECK_QUERY = db.session.query(Apple_Realtime_News).all()

        carousel = CarouselColumn(
                    thumbnail_image_url = 'https://imgur.com/ya0Vj4y.jpg',
                    title = '更多新聞',
                    text =  '請選擇',
                    actions = [
                        PostbackTemplateAction(
                            label='上一頁',
                            data = '蘋果新聞 '+str(len(CHECK_QUERY)-9)
                        ),
                        PostbackTemplateAction(
                            label=' ',
                            data = ' '
                        )
                    ]
                 )
        DATA.append(carousel)

        news_id = db.session.query(Apple_Realtime_News.id).all()
        sort_news = sorted(news_id)
        for x in sort_news[-9:]:
            QUERY = db.session.query(Apple_Realtime_News).filter(Apple_Realtime_News.id==x).first()
            time = QUERY.DATE
            title = QUERY.TITLE
            href = QUERY.URL
            image_url = QUERY.IMAGE_URL
            news_type = QUERY.NEWS_Type
            reply_data = reply_data + title + '\n' + href + '\n'
            A = CarouselColumn(
                    thumbnail_image_url = image_url,
                    title = title,
                    text =  news_type,
                    actions = [
                        URITemplateAction(
                           label = '瀏覽網頁',
                           uri = href
                        ),
                        PostbackTemplateAction(
                            label=' ',
                            data = ' '
                        )
                    ]
                 )
            DATA.append(A)


        carousel_template_message = TemplateSendMessage(
                alt_text = 'Carousel template',
                template = CarouselTemplate(DATA)
            )
        line_bot_api.reply_message(event.reply_token,carousel_template_message)

##################
    elif re.search('科技新聞', user_text):
        data = tech_crawler()
        reply_data=''
        for tech_news in data:
            reply_data = reply_data + tech_news['title'] + '\n' + tech_news['href'] + '\n'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_data))

####################
    elif re.search('新聞', user_text):

        buttons_template_message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                thumbnail_image_url='https://imgur.com/p6F5YU1.jpg',
                title='新聞',
                text='請選擇',
                actions = [
                    MessageTemplateAction(
                        label='蘋果新聞',
                        text='蘋果新聞'
                    ),
                    MessageTemplateAction(
                        label='科技新聞',
                        text='科技新聞'
                    )
                ]
            )    
        )
        line_bot_api.reply_message(event.reply_token,buttons_template_message)

####################

    elif user_text == '#delete':

        delete_data = CHECK_QUERY.first().Delete_Event

        delete = db.session.query(Notebook).filter(Notebook.id == delete_data).first()

        if delete == None :
            text = '找不到你要刪除的事件喔，你可能已經更改或刪除它了!'
        else :
            text = '已經幫你刪除囉~'
            db.session.delete(delete)
            db.session.commit()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text))

##################
    elif user_text == '我的課表':

        CHECK = str(set_data.Student_ID)

        QUERY_Exist = db.session.query(Elective_Data.Cource).filter(Elective_Data.Student_ID==CHECK).first()

        if CHECK == 0 or QUERY_Exist==None:
            QUERY = db.session.query(Calendar).all()
            date = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
            nowdays = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M')    
            
            EXAM1 = datetime.datetime(QUERY[1].Year + 1911 ,int(QUERY[1].Month), int(QUERY[1].Day), 0, 0)    
            EXAM2 = datetime.datetime(QUERY[3].Year + 1911 ,int(QUERY[3].Month), int(QUERY[3].Day), 0, 0)    
            
            CHECK =  timedelta(days=0)
            
            Source_1 = datetime.datetime(QUERY[-2].Year + 1911 ,int(QUERY[-2].Month), int(QUERY[-2].Day), 0, 0) 
            Source_2 = datetime.datetime(QUERY[-1].Year + 1911 ,int(QUERY[-1].Month), int(QUERY[-1].Day), 0, 0) 
            
            
            if (EXAM1 - nowdays > CHECK and Source_1 - nowdays < CHECK) or (EXAM2 - nowdays > CHECK and Source_2 - nowdays < CHECK):
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text='你還沒登入喔~'))
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text='請輸入你的學號~'))
                data = CHECK_QUERY.update({'Status':3,'Add_Index':1})
                db.session.commit()
            else:
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text='非開放時間喔~'))          
        else:
            QUERY_Cource = db.session.query(Elective_Data.Cource,Elective_Data.Number).filter(Elective_Data.Student_ID==CHECK).all()
            reply = ''
            MON=[]
            TUE=[]
            WED=[]
            THU=[]
            FRI=[]
            SAT=[]
            SUN=[]
            for cource in QUERY_Cource:
                QUERY_Cource_NUMBER = db.session.query(Cource).filter(Cource.Number==cource[0]).all()
                Number = ''
                if cource[1] != 0:
                    Number = str(cource[1])+'號'
                else:
                    Number = ''

                for COURCE in QUERY_Cource_NUMBER:
                    Cource_Week = COURCE.Week
                    if Cource_Week == '一':
                        MON.append((COURCE.SourceTime,COURCE,Number))
                    elif Cource_Week == '二':
                        TUE.append((COURCE.SourceTime,COURCE,Number))
                    elif Cource_Week == '三':
                        WED.append((COURCE.SourceTime,COURCE,Number))
                    elif Cource_Week == '四':
                        THU.append((COURCE.SourceTime,COURCE,Number))
                    elif Cource_Week == '五':
                        FRI.append((COURCE.SourceTime,COURCE,Number))
                    elif Cource_Week == '六':
                        SAT.append((COURCE.SourceTime,COURCE,Number))
                    elif Cource_Week == '日':
                        SUN.append((COURCE.SourceTime,COURCE,Number))

            reply_array = [MON,TUE,WED,THU,FRI,SAT,SUN]
            for week in reply_array:
                reply = ''
                if week != []:
                    for x in sorted(week):
                        reply = reply +x[1].Name + '\n'+x[1].Teacher + '\u3000' + x[2] +'\n' + x[1].Time+ '\n-------------\n'
                    reply = reply[:-15]
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text=reply))


####################################
    elif user_text == '淡江學生':
        remind_text = ''
        remind = CHECK_QUERY.first().Remind
        if remind:
            remind_text = '關閉提醒'
        else:
            remind_text = '開啟提醒'
        print(remind_text)
        buttons_template_message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                thumbnail_image_url='https://imgur.com/x8NQ4VI.jpg',
                title='淡江學生',
                text='請選擇',
                actions = [
                    MessageTemplateAction(
                        label='我的課表',
                        text='我的課表'
                    ),
                    MessageTemplateAction(
                        label='今天的課',
                        text='今天的課'
                    ),
                    MessageTemplateAction(
                        label='活動報名系統',
                        text='活動報名系統'
                    ),MessageTemplateAction(
                        label=remind_text,
                        text=remind_text
                    )
                ]
            )    
        )
        line_bot_api.reply_message(event.reply_token,buttons_template_message)

####################################

    elif user_text == '關閉提醒':
        CHECK = str(set_data.Student_ID)

        QUERY_Exist = db.session.query(Elective_Data.Cource).filter(Elective_Data.Student_ID==CHECK).first()

        if CHECK == 0 or QUERY_Exist==None:
            QUERY = db.session.query(Calendar).all()
            date = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
            nowdays = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M')    
            
            EXAM1 = datetime.datetime(QUERY[1].Year + 1911 ,int(QUERY[1].Month), int(QUERY[1].Day), 0, 0)    
            EXAM2 = datetime.datetime(QUERY[3].Year + 1911 ,int(QUERY[3].Month), int(QUERY[3].Day), 0, 0)    
            
            CHECK =  timedelta(days=0)
            
            Source_1 = datetime.datetime(QUERY[-2].Year + 1911 ,int(QUERY[-2].Month), int(QUERY[-2].Day), 0, 0) 
            Source_2 = datetime.datetime(QUERY[-1].Year + 1911 ,int(QUERY[-1].Month), int(QUERY[-1].Day), 0, 0) 
            
            
            if (EXAM1 - nowdays > CHECK and Source_1 - nowdays < CHECK) or (EXAM2 - nowdays > CHECK and Source_2 - nowdays < CHECK):
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text='你還沒登入喔~'))
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text='請輸入你的學號~'))
                data = CHECK_QUERY.update({'Status':3,'Add_Index':1})
                db.session.commit()
            else:
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text='非開放時間喔~'))  
        else:
            confirm = TemplateSendMessage(
                      alt_text='Confirm template',
                      template=ConfirmTemplate(
                          text= '按確認鍵，小幫手將關閉提醒服務，不會自動傳送課程資訊\n如需繼續使用，請按取消鍵',
                          actions = [
                              PostbackTemplateAction(
                                  label='確認',
                                  data='關閉提醒'
                              ),
                              PostbackTemplateAction(
                                  label='取消',
                                  data='#no'
                              )
                          ]
                      )
                  )
            line_bot_api.reply_message(event.reply_token,confirm)


    elif user_text == '開啟提醒':
        confirm = TemplateSendMessage(
                      alt_text='Confirm template',
                      template=ConfirmTemplate(
                          text= '按確認鍵，小幫手將開啟提醒服務，於上課前20分鐘自動傳送課程資訊\n如不需使用，請按取消鍵',
                          actions = [
                              PostbackTemplateAction(
                                  label='確認',
                                  data='開啟提醒'
                              ),
                              PostbackTemplateAction(
                                  label='取消',
                                  data='#no'
                              )
                          ]
                      )
                  )
        line_bot_api.reply_message(event.reply_token,confirm)

####################################
    elif user_text == '今天的課':

        CHECK = str(set_data.Student_ID)
        QUERY_Exist = db.session.query(Elective_Data.Cource).filter(Elective_Data.Student_ID==CHECK).first()
        if CHECK == 0 or QUERY_Exist==None:
            QUERY = db.session.query(Calendar).all()
            date = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
            nowdays = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M')    
            
            EXAM1 = datetime.datetime(QUERY[1].Year + 1911 ,int(QUERY[1].Month), int(QUERY[1].Day), 0, 0)    
            EXAM2 = datetime.datetime(QUERY[3].Year + 1911 ,int(QUERY[3].Month), int(QUERY[3].Day), 0, 0)    
            
            CHECK =  timedelta(days=0)
            
            Source_1 = datetime.datetime(QUERY[-2].Year + 1911 ,int(QUERY[-2].Month), int(QUERY[-2].Day), 0, 0) 
            Source_2 = datetime.datetime(QUERY[-1].Year + 1911 ,int(QUERY[-1].Month), int(QUERY[-1].Day), 0, 0) 
            
            
            if (EXAM1 - nowdays > CHECK and Source_1 - nowdays < CHECK) or (EXAM2 - nowdays > CHECK and Source_2 - nowdays < CHECK):
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text='你還沒登入喔~'))
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text='請輸入你的學號~'))
                data = CHECK_QUERY.update({'Status':3,'Add_Index':1})
                db.session.commit()
            else:
                line_bot_api.push_message(event.source.user_id,TextSendMessage(text='非開放時間喔~'))   
        else:
            QUERY_Cource = db.session.query(Elective_Data.Cource,Elective_Data.Number).filter(Elective_Data.Student_ID==CHECK).all()
            reply = ''
            check_time = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%w')
            week = ''
            if check_time == '0':
                week = '日'
            elif check_time == '1':
                week = '一'
            elif check_time == '2':
                week = '二'
            elif check_time == '3':
                week = '三'
            elif check_time == '4':
                week = '四'
            elif check_time == '5':
                week = '五'
            else:
                week = '六'

            sort = []

            for cou in QUERY_Cource:
                qurey = db.session.query(Cource).filter(Cource.Number==cou[0]).all()

                for cource in qurey:
                    if re.search(week,cource.Week):
                        Number = ''
                        if cou[1] != 0:
                            Number = str(cou[1])+'號'

                        sort.append((cource.SourceTime,cource,Number))  #加入今天的課

#                        reply = reply + cource.Name + '\n' + cource.Teacher+ '\u3000' + Number  + '\n' + cource.Time + '\n--------------------\n'


            for cource in sorted(sort):
                reply = reply + cource[1].Name + '\n' + cource[1].Teacher+ '\u3000' + cource[2] + '\n' + cource[1].Time + '\n--------------------\n'


            if reply == '':                    #排序課表時間
                reply = '今天沒有課喔'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply[:-22]))

####################################

    elif user_text == '活動報名系統':
        soup = connect('http://enroll.tku.edu.tw/') 
        tr = soup.find('table').find('tbody').find_all('tr')
        reply=''

        array = tr
        if len(tr)>10:
            array = tr[:11]
        else:
            array = tr

        for active in array:
            name = active.find_all('td')[2].text
            href = 'http://enroll.tku.edu.tw/' + active.find_all('td')[2].find('a')['href']
            reply = reply + name + '\n' + href
            if array[-1] == active:
                break
            else:
                reply = reply + '\n\n'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))

###################################
    elif user_text == '天氣':

        Weather = db.session.query(Weather_Data).first()

        humidity = Weather.Humidity
        temp = Weather.Temprature
        feel_temp = Weather.Feel_Temprature
        railfall_random = Weather.Railfall_Random
        weather = Weather.Weather_Status
        time = Weather.Time

        reply = '溫度: '+temp+'°C\n體感溫度: '+feel_temp+'°C\n濕度:'+humidity+'\n降雨機率: '+railfall_random+'\n天氣狀況:'+weather+'\n觀測地點: 淡水捷運站\n觀測時間: '+time

        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))

############################################

    elif user_text == '功能總覽':

        remind_text = ''
        remind = CHECK_QUERY.first().Remind
        if remind:
            remind_text = '關閉提醒'
        else:
            remind_text = '開啟提醒'

        carousel = [CarouselColumn(
                        thumbnail_image_url='https://imgur.com/x8NQ4VI.jpg',
                        title='淡江學生',
                        text='請選擇',
                        actions = [
                            MessageTemplateAction(
                                label='我的課表',
                                text='我的課表'
                            ),
                            MessageTemplateAction(
                                label='今天的課',
                                text='今天的課'
                            ),
                            MessageTemplateAction(
                                label='活動報名系統',
                                text='活動報名系統'
                            )        
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://imgur.com/x8NQ4VI.jpg',
                        title='淡江學生',
                        text='請選擇',
                        actions = [
                            MessageTemplateAction(
                                label=remind_text,
                                text=remind_text
                            ),  
                            MessageTemplateAction(
                                label='登出',
                                text='登出'
                            ),
                            URITemplateAction(
                                label='聯絡開發人員',
                                uri='https://www.facebook.com/tkulinebot/'
                            ) 
                        ]
                    ),CarouselColumn(
                        thumbnail_image_url='https://imgur.com/od2Qlu5.jpg',
                        title='我能幫你嗎??',
                        text='說說你的故事吧',
                        actions = [
                            PostbackTemplateAction(
                                label=' ',
                                data=' '
                            ),  
                            MessageTemplateAction(
                                label='我有什麼事',
                                text='#see'
                            ),
                            MessageTemplateAction(
                                label='幫我記事情',
                                text='#add'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://imgur.com/p6F5YU1.jpg',
                        title='新聞',
                        text='請選擇',
                        actions = [
                            PostbackTemplateAction(
                                label=' ',
                                data=' '
                            ),  
                            MessageTemplateAction(
                                label='蘋果新聞',
                                text='蘋果新聞'
                            ),
                            MessageTemplateAction(
                                label='科技新聞',
                                text='科技新聞'
                            ) 
                        ]
                    )
        ]

        carousel_template_message = TemplateSendMessage(
                alt_text = 'Carousel template',
                template = CarouselTemplate(carousel)
            )
        line_bot_api.reply_message(event.reply_token,carousel_template_message)

############################################
    elif user_text == '紅27 捷運淡水站':
        reply=''
        Reply = GetBusData('16671','0')
        for data in Reply:
            if data != Reply[-1]:
                reply = reply + data + '\n'
            else:
                reply = reply + data
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))

    elif user_text == '紅27 淡江大學':
        reply=''
        Reply = GetBusData('16671','1')
        for data in Reply:
            if data != Reply[-1]:
                reply = reply + data + '\n'
            else:
                reply = reply + data
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))

    elif user_text == '紅28 捷運淡水站':
        reply=''
        Reply = GetBusData('16288','1')
        for data in Reply:
            if data != Reply[-1]:
                reply = reply + data + '\n'
            else:
                reply = reply + data
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))

    elif user_text == '紅28 淡江大學':
        reply=''
        Reply = GetBusData('16288','0')
        for data in Reply:
            if data != Reply[-1]:
                reply = reply + data + '\n'
            else:
                reply = reply + data
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))

    elif user_text == '紅37 捷運淡水站':
        reply=''
        Reply = GetBusData('16431','0')
        for data in Reply[14:]:
            if data != Reply[-1]:
                reply = reply + data + '\n'
            else:
                reply = reply + data
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))

    elif user_text == '紅37 淡海新市鎮':
        reply=''
        Reply = GetBusData('16431','1')
        for data in Reply[:13]:
            if data != Reply[12]:
                reply = reply + data + '\n'
            else:
                reply = reply + data
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))

    elif user_text == '860 捷運淡水站':
        reply=''
        Reply = GetBusData('16528','0')
        for data in Reply[-11:]:
            if data != Reply[-1]:
                reply = reply + data + '\n'
            else:
                reply = reply + data
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))

    elif user_text == '860 三芝':
        reply=''
        Reply = GetBusData('16528','1')
        for data in Reply[:8]:
            if data != Reply[7]:
                reply = reply + data + '\n'
            else:
                reply = reply + data
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))
####################################
    elif user_text == '捷運淡水站到淡江大學':
        Red27 = GetBusData('16671','1')
        Red28 = GetBusData('16288','0')
        Red37 = GetBusData('16431','1')
        Bus860 = GetBusData('16528','1')
        reply = '紅27:\n'+Red27[0]+'\n紅28:\n'+Red28[0]+'\n紅37:\n'+Red37[0]+'\n860:\n'+Bus860[0]
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))

###################################
    elif user_text == '淡江大學到捷運淡水站':
        Red27 = GetBusData('16671','0')
        Red28 = GetBusData('16288','1')
        Red37 = GetBusData('16431','0')
        Bus860 = GetBusData('16528','0')
        reply = '紅27:\n'+Red27[0]+'\n紅28:\n'+Red28[0]+'\n紅37:\n'+Red37[-7]+'\n860:\n'+Bus860[-7]
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))

###################################
    elif user_text == '公車':
        carousel = [CarouselColumn(
                        thumbnail_image_url='https://imgur.com/5G3DPps.jpg',
                        title='公車',
                        text='請選擇要往哪個方向\n(本選單僅提供簡潔資訊）',
                        actions = [
                            MessageTemplateAction(
                                label='淡江大學',
                                text='捷運淡水站到淡江大學'
                            ),
                            MessageTemplateAction(
                                label='捷運淡水站',
                                text='淡江大學到捷運淡水站'
                            )
                        ]
                   ),CarouselColumn(
                        thumbnail_image_url='https://imgur.com/lLz66Br.jpg',
                        title='紅27',
                        text='請選擇要往哪個方向',
                        actions = [
                            MessageTemplateAction(
                                label='淡江大學',
                                text='紅27 淡江大學'
                            ),
                            MessageTemplateAction(
                                label='捷運淡水站',
                                text='紅27 捷運淡水站'
                            )
                        ]
                   ),
                   CarouselColumn(
                        thumbnail_image_url='https://imgur.com/5G3DPps.jpg',
                        title='紅28',
                        text='請選擇要往哪個方向',
                        actions = [
                            MessageTemplateAction(
                                label='淡江大學',
                                text='紅28 淡江大學'
                            ),
                            MessageTemplateAction(
                                label='捷運淡水站',
                                text='紅28 捷運淡水站'
                            )
                        ]
                   ),CarouselColumn(
                        thumbnail_image_url='https://imgur.com/lLz66Br.jpg',
                        title='紅37',
                        text='請選擇要往哪個方向',
                        actions = [
                            MessageTemplateAction(
                                label='淡海新市鎮',
                                text='紅37 淡海新市鎮'
                            ),
                            MessageTemplateAction(
                                label='捷運淡水站',
                                text='紅37 捷運淡水站'
                            )
                        ]
                   ),
                   CarouselColumn(
                        thumbnail_image_url='https://imgur.com/5G3DPps.jpg',
                        title='860',
                        text='請選擇要往哪個方向',
                        actions = [
                            MessageTemplateAction(
                                label='三芝',
                                text='860 三芝'
                            ),
                            MessageTemplateAction(
                                label='捷運淡水站',
                                text='860 捷運淡水站'
                            )
                        ]
                   )
        ]

        carousel_template_message = TemplateSendMessage(
                alt_text = 'Carousel template',
                template = CarouselTemplate(carousel)
            )
        line_bot_api.reply_message(event.reply_token,carousel_template_message)

############################################
    else:
        CHECK = str(set_data.Student_ID)
        
        if set_data.LINE_ID == 'U7c0e246866698ee90f0db29e7ca67807':  
            print('sudo')

            test = db.session.query(USER_DATA).all()



            
            print('end')
        else:
            print('Nothing')
############################################





def DetectionVidcode(img):
    
    kernal = np.ones((2,2),np.uint8)
    erosion = cv2.erode(img,kernal,iterations=1)
    rows, cols, dims = img.shape
    Y_plane = np.float32(np.zeros((rows,cols)))
    for i in range(0,rows):
        for j in range(0,cols):
            Y_plane[i,j] = np.float32(0.299*erosion[i,j,0] + 0.5877*erosion[i,j,1] + 0.114*erosion[i,j,2])

    opencv_img = np.array(erosion)
    imgray = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    image, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted([(c, cv2.boundingRect(c)[0]) for c in contours], key = lambda x:x[1])

    ary = []
    for (c,_) in cnts:
        (x,y,w,h) = cv2.boundingRect(c)
        if h == 15:
            ary.append((x,y,w,h))

    for id, (x,y,h,w) in enumerate(ary):
        img = Y_plane[y:y+15,x:x+11]
        cv2.imwrite('sample/'+str(id)+'.jpg', img)

    clf = joblib.load('captcha.pk1')
    basewidth = 50
    data = []
    cnt = 0

    for idx, img in enumerate(os.listdir('sample/')):
        pil_img = PIL.Image.open('sample/{}'.format(img)).convert('1')
        wpercent = (basewidth/float(pil_img.size[0]))
        hsize = int((float(pil_img.size[1]*float(wpercent))))
        img = pil_img.resize((basewidth,hsize),PIL.Image.ANTIALIAS)
        data.append([pixel for pixel in iter(img.getdata())])
    scaler = StandardScaler()
    scaler.fit(data)
    data_scaled = scaler.transform(data)
    CAP = clf.predict(data_scaled)    
    vidcode = ''
    for i in CAP:
        vidcode = vidcode + str(i)    
    print(vidcode)
    return vidcode


def GetExamTable(username,password):
    requests.packages.urllib3.disable_warnings()
    rs = requests.session()
    res = rs.get('https://sso.tku.edu.tw/NEAI/ImageValidate', stream = True)

    #cookies = rs.cookies.get_dict()

    with open('test.jpg', 'wb') as f:
        f.write(res.content)
    img = cv2.imread('test.jpg')
    
    vidcode = DetectionVidcode(img)
    pay = {
        'myurl':'http://sso.tku.edu.tw/aissinfo/emis/tmw0012.aspx',
        'ln':'zh_TW',
        'embed':'No',
        'logintype':'logineb',
        'username': username,
        'password': password,
        'vidcode': vidcode,
        'loginbtn':'登入'
    }



    #cookies = dict(cookies_are='working')
    #rs = requests.session()

    res = rs.post('https://sso.tku.edu.tw/NEAI/login2.do?action=EAI',cookies=rs.cookies,data=pay,verify = False)


    #cookies = rs.cookies.update(res.cookies)

    res2 = rs.get('http://sso.tku.edu.tw/aissinfo/emis/TMWC040.aspx',cookies=res.cookies,verify = False)

    print(res2)
    print('\n')

    res3 = rs.get('http://sso.tku.edu.tw/aissinfo/emis/TMWC040_result.aspx?YrSem=10622&stu_no=' + str(username),verify = False)

    #res3 = rs.get('http://sso.tku.edu.tw/aissinfo/emis/TMWC040_result.aspx?YrSem=10622&stu_no=' + username,verify = False)
    soup = BeautifulSoup(res2.text, 'html.parser')
    print(soup)

    AllData = soup.find('table',id='DataGrid1').find_all('tr')
    for tr in AllData[1:]:
        td = tr.find_all('td')

        try:
            if td[8].text.isdigit():
                subject = td[1].text[5:]
                Score_number = td[6].text
                day = td[7].text
                Time = td[9].text
                classroom = ''.join(re.split(' ',td[10].text))
                Seat_number = td[11].text
                print(subject, Score_number, day, Time, classroom, Seat_number)
        except:
            continue
    return


###########################################
def Get_Cource(VarCource):
    requests.packages.urllib3.disable_warnings()
    pay2 = {
         'func':'go',
         'R1':'7',
         'classno':VarCource
    }
    rs = requests.session()
    res = rs.post('http://esquery.tku.edu.tw/acad/query_result.asp',data=pay2,verify = False)
    soup = BeautifulSoup(res.text, 'html.parser')
    cource_query = soup.find_all('td')
    cource_array = []
    for cource_obj in cource_query[24:]:
        try:
            cource_exception = cource_obj.find('span')
            cource_array.append(cource_exception.text)
        except Exception as ex:
            cource_array.append(cource_obj.text)
    cource_obj = []
    cource_list = []
    for x in range(0,len(cource_array)+1):
        if(x%16!=0):
            cource_obj.append(cource_array[x])
        else:
            cource_list.append(cource_obj)
            cource_obj = []
    TIME=''
    Week=''
    for cource_data in cource_list[1:]:
        Week=''
        if cource_data[14] != '\u3000':
            TIME = cource_data[13] +'\n' + cource_data[14]
        else:
            TIME = cource_data[13]

        time_array = re.split('\n',TIME)

        for data in time_array:
             if data == '':
                 continue
             Time = re.split(' /',data)
             session_array = re.split(',',Time[1])
             array = []    
             for session in session_array:
                 if len(session_array) > 1:
                     ans = re.split(' ',session)    
                     for ANS in ans:        
                         if ANS == '':
                             continue
                         else:
                             if re.match('\u3000',ANS):
                                 ans = re.split('\u3000',ANS)
                                 array.append(ans[-1])
                             else:        
                                 ans = re.split(' ',ANS)
                                 for Ans in ans:
                                     if Ans == '':
                                         continue
                                     else:
                                         array.append(Ans)
                 else:
                     if re.match('\u3000',session):    
                         ans = re.split('\u3000',session)
                         array.append(ans[-1])
                     else:
                         ans = re.split(' ',session)
                         for Ans in ans:
                             if Ans == '':
                                 continue        
                             else:
                                 array.append(Ans)

             start = None
             Week = None
             TIME = None

             try:
                 start = int(array[0]) + 7
                 source = str(int(array[0]) + 7)
                 destination = str(int(array[-1]) + 8)

                 if len(source) == 1 :
                     source = '0' + source
                 if len(destination) == 1:
                     destination = '0' + destination
                 area = re.split(' ',Time[-1])
                 source_session = array[0]
                 destination_session = array[-1]

                 if len(source_session) == 1:
                     source_session = '0'+source_session
                 if len(destination_session) == 1:
                     destination_session = '0'+destination_session

                 if len(array) > 1:
                     session = source_session + '-' +destination_session
                 else:
                     session = source_session
                 source_time = '（'+Time[0]+'）' +session+'（' + source + ':10~'
                 destination_time = destination + ':00)'
                 classroom = '\n  ➤' + area[1] + area[-2]
                 TIME = source_time + destination_time + classroom
                 Week = Time[0]
             except:
                 start = None
                 Week = None
                 TIME = ' '
             insert_data = Cource(
                 Number = VarCource,
                 Teacher = re.split('\n',cource_data[12][:-8])[-1],
                 Name = re.split('\n',cource_data[10])[1],
                 Time = TIME,
                 Week = Week,
                 SourceTime = start
             )

             db.session.add(insert_data)
             db.session.commit()

def GetWeather():
    year = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%Y')
    rs = requests.session()
    res = rs.get('http://www.cwb.gov.tw/m/f/entertainment/GT/C049.htm?_=1518627446973',verify = False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    div = soup.find('div','center clearfix') 
    humidity = soup.find('ul','clearfix blueBack').find('span').text
    time = year + ' ' +div.find('span','today').text[:-5]
    feel_temp = div.find('div','AT').contents[1]
    temp = div.find('span','degree blue').contents[0]
    weather = div.find('p').text
    res2 = rs.get('http://www.cwb.gov.tw/m/f/entertainment/C049.php',verify = False)
    res2.encoding = 'utf-8'
    railfall_random = BeautifulSoup(res2.text, 'html.parser').find('div','tabbable').find_all('tr')[1].contents[9].text
    update_data = db.session.query(Weather_Data).update({'Humidity':humidity,'Temprature':temp,'Feel_Temprature':feel_temp,'Railfall_Random':railfall_random,'Weather_Status':weather,'Time':time})
    db.session.commit()

def GetCalendar():
    DELETE = db.session.query(Calendar).all()
    for i in DELETE:
        db.session.delete(i)
        db.session.commit()           
    requests.packages.urllib3.disable_warnings()
    rs = requests.session()
    res = rs.get('http://www.acad.tku.edu.tw/app/super_pages.php?ID=OAA201',verify = False)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, 'html.parser')
    Exam = []
    START = []
    for tbody in soup.find_all('tbody'):
        Tr = tbody.find_all('tr')
        for tr in Tr:
            if re.search('考試週',tr.text):
                Td = tr.find_all('td')
                Exam.append([''.join(re.split('\n',Td[1].text)),''.join(re.split('\n',Td[3].text))])
                
            if re.search('開始上課',tr.text):
                st = tr.find_all('td')
                START.append([''.join(re.split('\n',st[1].text)),''.join(re.split('\n',st[3].text))])
                
    for i in Exam:
        TIME = re.split('～',i[0])[0]
        NAME = i[1]
        SPLIT = re.split('/',TIME)
        Year = SPLIT[0]
        Month = SPLIT[1] 
        Day = SPLIT[2]
        insert_data = Calendar(
            Name = NAME,
            Year = int(Year),
            Month = Month,
            Day = Day
        )
        db.session.add(insert_data)
        db.session.commit()
    for j in START:
        NAME = j[1]
        SPLIT = re.split('/',j[0])
        Year = SPLIT[0]
        Month = SPLIT[1] 
        Day = SPLIT[2]
        insert_data = Calendar(
            Name = NAME,
            Year = int(Year),
            Month = Month,
            Day = Day
        )
        db.session.add(insert_data)
        db.session.commit()


def GetBusData(rid,sec):
    requests.packages.urllib3.disable_warnings()
    rs = requests.session()
    res = rs.get('http://routes.5284.com.tw/ntpcebus/Tw/Map?rid='+rid+'&sec='+sec,verify = False)
    soup = BeautifulSoup(res.text, 'html.parser')
    search = soup.find(id='map')
    stop = search.find_all('div','stopName')
    stopName_array = []
    Reply=[]
    for stopName in stop:
        stopName_array.append(stopName.text)
    res2 = rs.get('http://routes.5284.com.tw/ntpcebus/Js/RouteInfo?rid='+rid+'&sec='+sec,verify = False)
    data = json.loads(res2.text)
    Etas = data['Etas']
    for etas in Etas:
        idx = etas['idx']
        eta = etas['eta']
        etaString = '';
        if eta == 255:
            etaString = "\u3000(未發車)"
        elif eta == 254:
            etaString = "\u3000(末班車已過)"
        elif eta == 253:
            etaString = "\u3000(交管不停靠)"
        elif eta == 252:
            etaString = "\u3000(今日未營運)"
        elif eta == 251:
            etaString = "\u3000(未發車)"
        elif eta < 3:
            etaString = "\u3000(將到站)"
        else:
            etaString = "\u3000(約" + str(eta) + "分)"
        reply = '➤' + stopName_array[idx] + '\n' + etaString
        Reply.append(reply)
    return Reply

############################################

def confirm_template(title,label_1,text_1,label_2,text_2) :
    confirm_template_message = TemplateSendMessage(
        alt_text='Confirm template',
        template=ConfirmTemplate(
            text= title,
            actions = [
                PostbackTemplateAction(
                    label=label_1,
                    text=text_1,
                    data=text_1
                ),
                PostbackTemplateAction(
                    label=label_2,
                    text=text_2,
                    data=text_2
                )
            ]
        )
    )
    return confirm_template_message

#########################

def applenews_crawler():
    soup = connect('https://tw.appledaily.com/new/realtime')
    data = soup.find_all("li","rtddt")[:10][::-1]
    for x in data:
        if x.find('a').h1.font:
            url = x.find('a')['href']
            CHECK_QUERY = db.session.query(Apple_Realtime_News).filter(Apple_Realtime_News.URL == url).first()
            if CHECK_QUERY == None :
                time = x.find('a').time.text
                time = datetime.datetime.now().strftime('%Y-%m-%d ') + time
                news_type = x.find('a').find('h2').text
                soup2 = connect(url)

                try:
                    image_url = soup2.find('div','ndAritcle_headPic').find('img')['src']
                except Exception as ex:
                    try:
                        image_url = soup2.find('div','ndAritcle_margin').find('img')['src']
                    except Exception as ex:
                        try:
                            image_url = soup2.find('div','ndArticle_margin').find('img')['src']
                        except Exception as ex:
                            image_url = 'https://img.appledaily.com.tw/images/fb_sharelogo_1.jpg'
                title = soup2.find('article','ndArticle_leftColumn').find('hgroup').h1.text
                insert_data = Apple_Realtime_News(
                        TITLE = title,
                        DATE = time,
                        URL = url,
                        IMAGE_URL = image_url,
                        NEWS_Type = news_type
                )
                db.session.add(insert_data)
                db.session.commit()
            else:
                continue
        else:
            continue

def connect(url):
    rs = requests.session()
    requests.packages.urllib3.disable_warnings()
    res = rs.get(url, verify = False)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup


def tech_crawler():
    soup = connect('https://technews.tw/')
    articles = []  # 儲存取得的文章資料
    tds = soup.find_all("td","maintitle")
    # 取得文章連結及標題
    for t in tds:
        if t.find('a'):  # 有超連結，表示文章存在，未被刪除
            title = t.find('a').string
            href = t.find('a')['href']
            articles.append({
                  'title': title,
                  'href': href
                })
    return articles

if __name__ == "__main__":
    print('@@')
    app.run(debug=True)
