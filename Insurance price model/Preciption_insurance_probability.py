import pymysql
import pandas as pd
import numpy as np
from scipy import stats

'''
保险公司给定保额保费比，给出每周最多赔偿1次，按月售卖的降雨险方案

'''
def dataexport(Date, Elements, Sitelist):
    conn = pymysql.connect(host='###', user='###', passwd='###', db='weatherhistory')
    cur = conn.cursor()
    df=pd.DataFrame()
    for i in Date:
        cur.execute("SELECT %s FROM ViewHistory%s where Siteid in (%s)"%(Elements[0],i,Sitelist))
        r = cur.fetchall()
        rdf = pd.DataFrame(list(r))
        rdf = rdf.replace(32700,0)
        year = pd.DataFrame([i[:4]]*len(r))
        month = pd.DataFrame([i[4:]]*len(r))
        rdf = pd.concat([rdf,year,month],axis=1)
        df = df.append(rdf)
        print(i)
    df.columns = Elements[0].split(',')+['Year','Month']
    y = df.pop('Year')
    m = df.pop('Month')
    df.insert(1, 'Year', y)
    df.insert(2, 'Month', m)
    return df


def chartname(mon):
    Date=[]
    for year in range(1986, 2016, 1): #生成匹配数据表名
        for m in mon:
            date=str(year)+str(m)
            Date.append(date)
    return Date


def P_level(x):
    P_thres = [0.1, 10, 25, 50, 100, 250, 9999]
    for i in range(len(P_thres)-1):
        if (x >= P_thres[i]) & (x < P_thres[i+1]):
            level = i+1
            break
        else:
            level = 99
    return level


def division(line):
    if line[1] in [1, 3, 5, 7, 8, 10, 12]:
        return round(line[3] / 930, 4)
    elif line[1] in [4, 6, 9, 11]:
        return round(line[3] / 900, 4)
    elif line[1] in [2]:
        return round(line[3] / 844, 4)


def supply(df):
    # 未出现过39℃但出现过41℃，将39-40℃的概率用38℃的概率替代
    for i in range(len(df)-1):
        if (df.iloc[i, 0] == df.iloc[i+1, 0]) & (df.iloc[i, 1] == df.iloc[i+1, 1]) & (df.iloc[i, 2] != df.iloc[i+1, 2]-1):
            above = df.iloc[:i+1]
            below = df.iloc[i+1:]
            df = above.append(pd.DataFrame([[df.iloc[i, 0], df.iloc[i, 1],
                                                      df.iloc[i, 2] + 1, df.iloc[i, 3]]],
                                            columns=df.columns), ignore_index=True).append(below, ignore_index=True)
    return df


def complete_table(df):
    # 构造一个包含每月包含各个阈值级别的表格
    s = df.drop_duplicates(['SiteId'])['SiteId']
    l1 = []
    l2 = []
    l3 = []
    for si in s:
        for m in range(1,13,1):
            for i in range(1,7,1):
                t1 = [si, m, i]
                l1.append(t1)
            for j in range(30, 43, 1):
                t2 = [si, m, j]
                l2.append(t2)
            for k in range(10, -16, -1):
                t3 = [si, m, k]
                l3.append(t3)
    db_p = pd.DataFrame(l1, columns=['SiteId', 'Month', 'level'])
    db_ta = pd.DataFrame(l2, columns=['SiteId', 'Month', 'level'])
    db_ti = pd.DataFrame(l3,columns=['SiteId', 'Month', 'level'])
    return db_p, db_ta, db_ti


def probability(df, P_level=P_level, supply=supply, complete_table=complete_table):

    df = df.reset_index(drop=1)
    df.iloc[:, 4:] = df.iloc[:, 4:]/10
    df['Month'] = df['Month'].astype('int')


    # 将每天的降水量、气温转为等级
    df['Prec_level'] = df['Precipitation20_20'].apply(P_level)

    # 统计每个等级每个月出现的次数，并计算出每个月出现1天该等级的概率
    df_group_P = df[['SiteId', 'Year', 'Month', 'Prec_level']].groupby(['SiteId', 'Month', 'Prec_level'], as_index=0).count()
    df_group_P = df_group_P[df_group_P['Prec_level'] < 99]
    df_group_P['Prob'] = df_group_P.apply(division, axis=1)
    df_group_P = df_group_P[['SiteId', 'Month', 'Prec_level', 'Prob']]
    df_group_P = df_group_P.sort_values(['SiteId', 'Month', 'Prec_level'], ascending=[1, 1, 0])
    #df_group_P = supply(df_group_P)

    # 构造完整阈值级别表格，补充概率为0的部分
    db_p, db_ta, db_ti = complete_table(df_group_P)
    df_prec = pd.merge(db_p, df_group_P, left_on=['SiteId', 'Month', 'level'], right_on=['SiteId', 'Month', 'Prec_level'],
                       how='left').drop(['Prec_level'], axis=1)
    df_prec = df_prec.fillna(0)
    df_prec = df_prec.sort_values(['SiteId', 'Month', 'level'], ascending=[1, 1, 0])
    return df_prec


# 概率累加大雨以上，-10度以下……
def rolling(df, window):
    prob = pd.Series()
    for s in df.drop_duplicates(['SiteId'])['SiteId']:
        for m in range(1, 13, 1):
            t = df[(df['SiteId'] == s) & (df['Month'] == m)]['Prob'].rolling(window, 1).sum()
            prob = prob.append(t)
    return prob


def match_payment(df1):
    thres = []
    for site in df1.drop_duplicates(['SiteId'])['SiteId']:
        for month in range(1, 13, 1):
            if month in [1, 3, 5, 7, 8, 10, 12]:
                n = 31
            elif month in [4, 6, 9, 11]:
                n = 30
            elif month in [2]:
                n = 28
            a = df1[(df1['SiteId'] == site) & (df1['Month'] == month)].reset_index(drop=1)
            l = [site, month, 999999, 999999, 999999, 999999, 999999, 999999]
            t = 100
            for i in range(len(a)):
                pl = stats.binom.pmf(list(range(1,8)), 7, a['Prob'][i])
                payment = 7/(n*sum(pl))
                p = abs(payment - n/7)
                if p < t:
                    t = p
                    l = [site, month, a['level'][i], a['Prob'][i], payment]
            thres.append(l)
    result = pd.DataFrame(thres, columns=['SiteId', 'Month', 'P_level', 'P_prob', 'Payment'])
    return result


# 输入参数
mon = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
Sitelist = open(r'D:\project\Bussiness\ZhongAn\XiaoNiu\sites.txt').read()
Elements = ['SiteId,Day,Precipitation20_20']

payment = [10, 20, 30]
Date = chartname(mon)
df = dataexport(Date, Elements, Sitelist)
df_prec = probability(df, Sitelist, Elements)
df_prec['Prob'] = rolling(df_prec, 6)
df_prec['Prob'] = df_prec['Prob'].replace(0, 0.001)

rdf = match_payment(df_prec)
rdf.to_csv(r'result20170317.csv',index=0)

