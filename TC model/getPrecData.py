import pymysql
import pandas as pd
import time
import numpy as np

'''
通过sites_match.py获取的台风影响站点及影响时间，
再通过此程序抽取该站点和时间对应的气象观测数据，
并将数据应用于20*20km的网格中
'''


def get_data(df):
    conn = pymysql.connect(host='###', user='###',
                           passwd='###', db='weatherhistory')
    df.columns =['id', 'TyphoonID', 'obs_time', 'site_id', 'distance']
    sign = 0
    prec = []
    sites = []
    dataid = []
    for i in range(len(df)):
        timeArray = time.strptime(df.obs_time[i], "%Y/%m/%d %H:%M:%S")
        day = str(timeArray.tm_mday)
        year = timeArray.tm_year
        month = timeArray.tm_mon
        if month < 10: month = '0'+str(month)
        YM = str(year)+str(month)
        site = df.site_id[i]
        cur = conn.cursor()
        cur.execute("SELECT	SiteId,	Precipitation20_20 FROM "
                    "ViewHistory%s WHERE SiteId = %s AND `day` = %s"
                    % (YM, site, day))
        r = cur.fetchall()
        if len(r) > 0:
            prec.append(r[0][1])
            sites.append(r[0][0])
            dataid.append(df.id[i])
        else:
            prec.append(999999)
            sites.append(df.site_id[i])
            dataid.append(df.id[i])
        sign += 1
        if sign % 1000 == 0:
            print(sign)
    cur.close()
    conn.close()

    result = [sites, dataid, prec]
    df_meteo = pd.DataFrame(result)
    df_meteo = df_meteo.T
    df_meteo.columns = ['site_id', 'id', 'prec']
    df_result = pd.merge(df, df_meteo, on=['site_id', 'id'])
    df_result['prec'] = df_result['prec']/10
    return df_result


df = pd.read_csv(r'sites_match.csv')


def risk_assess(get_data=get_data):
    df_result = get_data(df)
    df_result['obs_time'] = pd.to_datetime(df_result['obs_time'])
    df_result['month'] = df_result['obs_time'].apply(lambda x: x.month)
    df_result['day'] = df_result['obs_time'].apply(lambda x: x.day)
    df_result['prec'] = df_result['prec'].replace(3270, 0)

    df_prob_50 = df_result[(df_result['prec'] >= 50) & (df_result['prec'] <= 100)]\
    [['siteId', 'month', 'prec']].groupby(['siteId', 'month'], as_index=0).count()
    df_prob_50['level'] = 1

    df_prob_100 = df_result[(df_result['prec'] >= 100) & (df_result['prec'] <= 250)]\
    [['siteId', 'month', 'prec']].groupby(['siteId', 'month'], as_index=0).count()
    df_prob_100['level'] = 2

    df_prob_250 = df_result[df_result['prec'] >= 250][['siteId', 'month', \
                'prec']].groupby(['siteId', 'month'], as_index=0).count()
    df_prob_250['level'] = 3
    df_prob = pd.concat([df_prob_50,df_prob_100,df_prob_250],axis=0)
    df_prob.iloc[:, 2] = df_prob.iloc[:, 2]/58

    sites = df_prob['siteId'].drop_duplicates()
    full_list = []
    for s in sites:
        for m in range(4, 12):
            for l in range(1, 4):
                full_list.append([s, m, l])
    df_list = pd.DataFrame(full_list, columns=['siteId', 'month', 'level'])
    df_full = pd.merge(df_list, df_prob, on=['siteId', 'month', 'level'], how='left')
    siteToGrid = pd.read_excel(r'siteIdToGrid.xlsx')

    gridList = []
    for s in siteToGrid['gridId']:
        for m in range(4, 12):
            for l in range(1, 4):
                gridList.append([s, m, l])
    df_grid = pd.DataFrame(gridList, columns=['gridId', 'month', 'level'])
    df_grid = pd.merge(df_grid, siteToGrid, on=['gridId'], how='left')
    df = pd.merge(df_grid,df_full, on=['siteId', 'month', 'level'], how='left')

    #len(df[~np.isnan(df['prec'])])/len(df)
    return df
df_risk = risk_assess()
df_risk.to_csv(r'prec.csv', index=0)

