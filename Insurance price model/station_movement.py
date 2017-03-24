# -*- coding: utf-8 -*-
import pandas as pd
import os

'''
站点元数据处理，提取气象站迁址信息
'''
walk = list(os.walk(r'data_sets'))
df = pd.DataFrame()
for i in range(1, len(walk)):
    w = walk[i]
    p = w[0]
    for fn in w[2]:
        if fn[-3:].lower() == 'txt':
            SiteId = fn[2:7]
            full_path = p + '\\' + fn
            try:
                file = open(full_path, encoding='utf8').read()
            except UnicodeDecodeError:
                print('错误出在目录%s的%s文件' % (p, fn))
                file = open(full_path).read()

            file_spl = file.strip().split('\n')
            for j in range(len(file_spl)):
                spl = file_spl[j].strip().split('/')
                if (spl[0] == '05') | (spl[0] == '55'):
                    fr = spl[1]
                    en = spl[2]
                    try:
                        lat = int(spl[3][:-1])/100
                        lon = int(spl[4][:-1])/100
                    except ValueError:
                        lat = 0
                        lon = 0
                    height = spl[5]
                    address = spl[6]
                    env = spl[7]
                    try:
                        mv = spl[8].split(';')[0]
                        dir = spl[8].split(';')[1]
                    except IndexError:
                        mv = 0
                        dir = 0
                    df = df.append([[SiteId, fr, en, lat, lon, height, address, env, mv, dir]])

df.columns = ['SiteId', 'start_time', 'end_time', 'latitude', 'longitude', 'height', 'address', 'enviroment', 'distance', 'direction']
df.to_csv(r'station_movement.csv', index=0)
