#!/usr/bin/env python
# encoding: utf-8
'''
@author: Ricardo
@license: (C) Copyright 2018-2019 @yang.com Corporation Limited.
@contact: 659706575@qq.com
@software: made@Yang
@file: get_license.py
@time: 2019/1/21 0021 14:11
@desc:
'''

import cv2
from hyperlpr import *
import matplotlib.pyplot as plt
import numpy,time
from PIL import Image, ImageDraw, ImageFont
import os,MySQLdb
from aip import AipSpeech

def speech_word(label):
    """语音识别模块 """
    APP_ID = '14250781'
    API_KEY = 'R6pTMXhz8apjC17W9r2pG0Ml'
    SECRET_KEY = 'n1svMyhjGKbNNQzZ4zCZvxH14NyDuGuk'

    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    result = client.synthesis(label, 'zh', 1, {
        'vol': 5, 'per': 4
    })

    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    if not isinstance(result, dict):
        with open('auido.mp3', 'wb') as f:
            f.write(result)

flag=0
def save_database(label):
    global flag
    db = MySQLdb.connect('localhost','root','1234','news',charset='utf8')
    cursor = db.cursor()
    ntime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    sql = "insert into plate(label,ntime) VALUES (%s,%s)"
    print('in...', ntime, label, flag)
    try:
        if flag != label:
            print('saving.....',label,flag)
            cursor.execute(sql,[label,ntime])
            db.commit()
            flag = label
            speech_word(label)
            os.system('auido.mp3')
    except Exception as e:
        print(e)
        db.rollback()
    db.close()



def cv2ImgAddText(img, text, r, textColor=(255, 255, 0), textSize=25):
    if (isinstance(img, numpy.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype("SimHei.ttf", textSize, encoding="utf-8")
    print('add text....',r, text)
    draw.text(r, text, textColor, font=fontText)
    return cv2.cvtColor(numpy.asarray(img),cv2.COLOR_RGB2BGR)

def get_image():
    image = cv2.imread('demo.jpg')
    result = HyperLPR_PlateRecogntion(image)
    label = result[0][0]
    score = result[0][1]
    r1 = tuple(result[0][2][0:2])
    br = tuple(result[0][2][-2:])
    # print(result,label,score,r1,br)
    img = cv2.rectangle(image,r1,br,(255,0,0),2)

    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    cv2ImgAddText(img,label,br[0]/2,r1[1])
    plt.imshow(img)
    plt.show()

def get_video():
    capture = cv2.VideoCapture(0)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    while True:
        try:
            print('video.....')
            stime = time.time()
            ret, frame = capture.read()
            results = HyperLPR_PlateRecogntion(frame)
            print(results)
            if ret:
                for result in results:
                    # print(result)
                    label = result[0]
                    score = result[1]
                    l1 = result[2]
                    # print(label,type(label),ql1,type(l1))
                    r1 = (l1[0],l1[1])
                    br = (l1[2],l1[3])
                    # print(r1,br)
                    speech_word(label)
                    img = cv2.rectangle(frame,r1,br,(255,0,0),2)

                    img = Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
                    frame = cv2ImgAddText(img,label,r1)

                    save_database(label)
                    # frame = cv2.putText(frame, label, r1, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)

                cv2.imshow('frame', frame)
        except Exception as e:
            print(e)
            pass
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    capture.release()
    cv2.destroyAllWindows()

get_video()
# get_image()

