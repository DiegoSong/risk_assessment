# encoding=utf8
import lmoments
import numpy as np
import copy
import datetime
import pandas as pd
import pymysql

'''
基于广义极值分布拟合的重现期模型
'''
def data_export(Date,Elements,Sitelist):
    conn = pymysql.connect(host='###', user='###', passwd='###', db='###')
    cur = conn.cursor()
    df=pd.DataFrame()
    for i in Date:
        cur.execute("SELECT %s FROM obsDay%s where Siteid in (%s)"%(Elements[0],i,Sitelist))
        r = cur.fetchall()
        rdf = pd.DataFrame(list(r))
        rdf = rdf.replace(32700,0)
        year = pd.DataFrame([i[:4]]*len(r))
        month = pd.DataFrame([i[4:]]*len(r))
        rdf = pd.concat([rdf,year,month],axis=1)
        df = df.append(rdf)
        print(i)
    df.columns = Elements[0].split(',')+['Year', 'Month']
    y = df.pop('Year')
    m = df.pop('Month')
    df.insert(1,'Year', y)
    df.insert(2,'Month', m)
    df = df.reset_index(drop=1)
    return df


def chartname(mon):
    Date=[]
    for year in range(1961,2016,1): #生成匹配数据表名
        for m in mon:
            date=str(year)+str(m)
            Date.append(date)
    return Date


def rep_err_data(p):
    if p > 3000:return 0
    else:return p


def match_days(obs_time):
    if (obs_time.year%4 == 0 and (obs_time.year%100 != 0 or obs_time.year%400 == 0)) and int(obs_time.strftime('%j'))>=60:
        return int(obs_time.strftime('%j'))-1
    else: return int(obs_time.strftime('%j'))


def enlarge_time_series(v0):
    # enlarge time series, 2 days before and after
    vb1 = copy.deepcopy(v0)
    vb1[1:365] = v0[0:364]
    vb1[0] = v0[364]

    vb2 = copy.deepcopy(v0)
    vb2[2:365] = v0[0:363]
    vb2[0:2] = v0[363:365]

    va1 = copy.deepcopy(v0)
    va1[0:364] = v0[1:365]
    va1[364] = v0[1]

    va2 = copy.deepcopy(v0)
    va2[0:363] = v0[2:365]
    va2[363:365] = v0[0:2]

    # merge
    v1 = np.hstack((vb2, vb1, v0, va1, va2))
    return v1


def data_formating(Elements, Sitelist, mon,chartname=chartname,data_export=data_export):
    Date = chartname(mon)
    df = data_export(Date, Elements, Sitelist)
    df['obs_time'] = pd.to_datetime(df[['Year','Month','Day']])
    df = df.drop(df[(df['Month']=='02')&(df['Day']==29)].index)
    df['days'] = df['obs_time'].apply(match_days)
    df[df['days']==0]
    df['Precipitation20_20'] = (df['Precipitation20_20']/10).apply(rep_err_data)
    df_order = df.pivot_table(values=['Precipitation20_20'],index=['days'],columns=['Year'], margins=True)
    v0 = np.array(df_order)
    return v0


# 广义极值分布拟合
def gev(x):
    param = lmoments.pelgev(lmoments.samlmu(x))
    return param


# 预测
def cdf(x, thres=thres):
    probs = []
    for t in thres:
        prob = lmoments.cdfgev(t,x)
        probs.append(prob)
    return probs

def main():
    # input sector
    Sitelist = '54511, 58367'
    Elements = ['SiteId,Day,Precipitation20_20']
    mon = ['01','02','03','04','05','06','07','08','09','10','11','12']

    # different threshold
    thres = [0.1, 10, 25, 50, 100, 250]
    np2 = len(thres)
    ndays = 365
    dims = v0.shape
    nyrs = dims[1]
    v0 = data_formating(Elements, Sitelist, mon)
    v1 = enlarge_time_series(v0)

    # 拟合广义极值分布并获得不同阈值下的概率
    params = np.apply_along_axis(gev, 1, v1)
    rp = np.apply_along_axis(cdf, 1, params)
    rp = 1-rp

    # 整理时间格式
    date = [datetime.datetime.strftime(datetime.datetime.strptime('2015-01-01', "%Y-%m-%d") + datetime.timedelta(i), "%m-%d") for i in xrange(365)]
    df_rp = pd.DataFrame.from_records(rp, index=date,columns=thres)
    df_rp.to_csv('/home/wisadmin/sd/Model/RP/result/rp_prec.csv',index=0)


