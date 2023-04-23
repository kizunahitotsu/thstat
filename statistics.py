import os
import re
import time
import json
import PySimpleGUI as sg

config_file='config.json'
data_file='data.json'

with open(config_file,mode='r',encoding='UTF-8') as f:
    config=json.load(f)

with open(data_file,mode='r',encoding='UTF-8') as f:
    data=json.load(f)

config={
    'Name':'雪莲华4BOSS',
    'Chapters':[
        '1非',
        '南北',
        '亡灯',
        '2非',
        '曼珠沙华',
        '双子星',
        '生命悬线',
    ],
    'Keyboards':[
        '笔记本薄膜',
        'B820R光轴',
        'DK68茶轴',
    ],
}

data={
    'Datas':[
        {
        'Date':'2023-04-23',
        'Keyboard':'DK68茶轴',
        'Result':[
            [0,1,1,1,1,0,1],
        ],
        },
    ],
    'Total':[
        0,0,0,0,0,0,0,
    ],
}


def test():
    with open(config_file,mode='w+',encoding='UTF-8') as f:
        json.dump(config,f,separators=(',',':'),indent=4,ensure_ascii=False)

    with open(data_file,mode='w+',encoding='UTF-8') as f:
        json.dump(data,f,separators=(',',':'),indent=4,ensure_ascii=False)

test()
print(time.strftime('%Y-%m-%d',time.localtime()))
