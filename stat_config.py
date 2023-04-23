import os
import re
import time
import json


def load_config(config_path):
    """
    load config from a json file
    :param config_path: the path to the config file
    :return: a tuple of (config, data)
    """
    data_path = f'{config_path}.data.json'
    with open(config_path, mode='r', encoding='UTF-8') as f:
        config = json.load(f)

    # ensure data file exists
    if not os.path.exists(data_path):
        data = {
            'Data': [],
            'Total': [0] * len(config['Chapters']),
        }
        with open(data_path, mode='w+', encoding='UTF-8') as f:
            json.dump(data, f, separators=(',', ':'), indent=4, ensure_ascii=False)

    # load data
    with open(data_path, mode='r', encoding='UTF-8') as f:
        data = json.load(f)
    return config, data


# config={
#     'Name':'雪莲华4BOSS',
#     'Chapters':[
#         '1非',
#         '南北',
#         '亡灯',
#         '2非',
#         '曼珠沙华',
#         '双子星',
#         '生命悬线',
#     ],
#     'Keyboards':[
#         '笔记本薄膜',
#         'B820R光轴',
#         'DK68茶轴',
#     ],
# }
#
# data={
#     'Data':[
#         {
#         'Date':'2023-04-23',
#         'Keyboard':'DK68茶轴',
#         'Result':[
#             [0,1,1,1,1,0,1],
#         ],
#         },
#     ],
#     'Total':[
#         0,0,0,0,0,0,0,
#     ],
# }
#
#
# def test():
#     with open(config_file,mode='w+',encoding='UTF-8') as f:
#         json.dump(config,f,separators=(',',':'),indent=4,ensure_ascii=False)
#
#     with open(data_file,mode='w+',encoding='UTF-8') as f:
#         json.dump(data,f,separators=(',',':'),indent=4,ensure_ascii=False)
#
# test()
# print(time.strftime('%Y-%m-%d',time.localtime()))
