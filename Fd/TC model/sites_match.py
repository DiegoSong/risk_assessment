import sys
import pandas as pd
import copy
import time
dir = r'D:\project\Fd\TC model'
sys.path.append(dir)
from distCount import distance


def data_clean():
    # 清洗文本数据
    raw_data = open(r'D:\project\Fd\TC model\best_track\cb.txt').read()
    raw_data = raw_data.strip().split('\n')
    data_struct = []
    for i in raw_data:
        d = i.strip().split()
        data_struct.append(d)

    data_onefile = []
    for j in range(len(data_struct)):
        if len(data_struct[j]) > 7:
            typhoon_id = copy.deepcopy(data_struct[j][4])
        else:
            tmp = copy.deepcopy(data_struct[j])
            tmp.insert(0, str(typhoon_id))
            data_onefile.append(tmp)
    df_structed = pd.DataFrame(data_onefile)
    df_structed.columns = ['ID', 'obs_time', 'TYPE', 'LAT', 'LON', 'PRES', 'WND', 'OWD']

    # 将数据中的时间格式化
    ot = []
    for i in df_structed.obs_time:
        timeArray = time.strptime(str(i), "%Y%m%d%H")
        ti = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
        ot.append(ti)
    dfot = pd.DataFrame(ot)
    df = pd.concat([df_structed, dfot], axis=1)
    df = df.drop('obs_time', axis=1)
    df.columns = ['ID','TYPE','LAT','LON','PRES','WND', 'OWD','obs_time']
    ti = df.pop('obs_time')
    df.insert(1, 'obs_time', ti)
    df['LAT'] = df['LAT'].astype('int')/10
    df['LON'] = df['LON'].astype('int')/10
    return df


def matchsiteid(data, sitelist): #取出受影响的气象站点，目前设定的是距中心100km以内
    resultlist = []
    sign = 0
    for i in range(len(data)):
        lat1 = data['LAT'][i]
        lon1 = data['LON'][i]
        for j in range(len(sitelist)):
            lat2 = sitelist['lat'][j]
            lon2 = sitelist['lon'][j]
            d = distance(lat1,lon1,lat2,lon2)
            if d <= 150:
                rl = copy.deepcopy(["%s"%data['ID'][i],"%s"%data['obs_time'][i],"%s"%sitelist['siteid'][j],"%s"%d])
                resultlist.append(rl)
        sign += 1
        if sign % 100 == 0:
            print(sign)
    relist = pd.DataFrame(resultlist)
    relist.columns = ['ID', 'obsTime', 'siteId', 'distance']
    return relist

df = data_clean()
sites = pd.read_excel(r'D:\project\Fd\TC model\Sitelist.xlsx')
sites_match = matchsiteid(df, sites)
sites_match.to_csv(r'D:\project\Fd\TC model\sites_match.csv')

