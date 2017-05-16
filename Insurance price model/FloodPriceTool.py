# -*- coding: utf-8 -*-
import lmoments
import pandas as pd
import pymysql
import numpy as np
import time

'''
    - 保费定价工具Version 0.0.1
    - 可用于计算连续一段时间累积降水，累积温度相关保险产品的价格
    - 可调整的输入项：
        1. 简单赔付率
        2. 重现期第1年的年数
        3. 城市
        4. 时间段（起始，终止）
        5. 要素（降水、温度）
    - 输出单城市5个阶梯的阈值，并将赔付率控制在100%
'''

# 根据输入的站点号及起止时间提取数据
def data_export(elements, site_id, start, end):
    conn = pymysql.connect(host='123.56.193.234', user='wis02', passwd='sini12#op', db='observe_siteId')
    cur = conn.cursor()
    cur.execute("SELECT {element} FROM obsSiteId where Siteid in ({site})".format(element=elements, site=site_id))
    r = cur.fetchall()
    rdf = pd.DataFrame(list(r))
    rdf = rdf.replace(32700, 0)
    rdf.columns = elements.split(',')
    rdf.iloc[:, 2] = rdf.iloc[:, 2]/10
    rdf.index = rdf.DateTime
    rdf = rdf.drop(['DateTime'], axis=1)
    period = pd.date_range(start, end, freq='D')
    for i in range(1, 31):
        period_tmp = pd.date_range(start, end, freq='D') - pd.tseries.offsets.DateOffset(years=i)
        period = period.append(period_tmp)
    df_select = rdf[rdf.index.isin(period)]
    df_select.insert(1, 'Year', df_select.index.year)
    df_select.insert(2, 'Month', df_select.index.month)
    df_select.insert(3, 'Day', df_select.index.day)
    return df_select.reset_index(drop=1)


# 输入项
class InfoInput():

    # 输入简单赔付
    def input_spr(self):
        while True:
            r = raw_input(' 5档简单赔付率为： 110%，200%，300%，500%，1000% \n\n 输入Y确认，输入N重新填写： '.decode('utf-8').encode('gbk'))
            if r == 'Y':
                s_mat = np.array([1.1, 2, 3, 5, 10])
                break
            elif r == 'N':
                s_mat = np.array(input(' 请重新输入并以逗号分隔： '.decode('utf-8').encode('gbk')))
                if len(s_mat) != 5:
                    print(' 赔付率输入有误, 请重新输入！'.decode('utf-8').encode('gbk'))
                else:
                    break
            else:
                print (' 输入有误,请重新输入！'.decode('utf-8').encode('gbk'))
        return s_mat

    # 输入年数
    def input_year(self):
        while True:
            try:
                t = input('\n 请输入第1个重现期年数： '.decode('utf-8').encode('gbk'))
                break
            except BaseException:
                print(' 年数输入有误，请重新输入！'.decode('utf-8').encode('gbk'))
        return t

    # 输入城市
    def input_city(self, lst):
        while True:
            try:
                c = raw_input('\n 请输入城市名： '.decode('utf-8').encode('gbk'))
                site = lst[lst['city_cn'] == c.decode('gbk')]['history_site_id'].values[0]
                break
            except BaseException:
                print(' 城市输入有误，请重新输入！'.decode('utf-8').encode('gbk'))
        return c.decode('gbk'),site

    # 输入时间
    def input_time(self):
        while True:
            try:
                ts_input = raw_input('\n 请输入起始时间，格式为 2017-6-7：'.decode('utf-8').encode('gbk')).decode('gbk')
                ts_f = time.strptime(ts_input, "%Y-%m-%d")
                break
            except BaseException:
                print(' 起始时间输入有误，请重新输入！'.decode('utf-8').encode('gbk'))
        while True:
            try:
                te_input = raw_input('\n 请输入终止时间，格式为 2017-6-7：'.decode('utf-8').encode('gbk')).decode('gbk')
                te_f = time.strptime(te_input, "%Y-%m-%d")
                if te_f < ts_f:
                    raise BaseException
                break
            except BaseException:
                print(' 终止时间输入有误，请重新输入！'.decode('utf-8').encode('gbk'))
        return ts_input, te_input

    # 输入要素
    def input_ele(self):
        while True:
            e_input = raw_input('\n 请输入要素，温度或降水：'.decode('utf-8').encode('gbk')).decode('gbk')
            if e_input == u'降水':
                elements = 'SiteId,DateTime,prec20_20'
                break
            elif e_input == u'温度':
                elements = 'SiteId,DateTime,tempAvg'
                break
            else:
                print(' 要素输入有误，请重新输入！'.decode('utf-8').encode('gbk'))
        return elements


# 计算重现期
class GEV(object):

    def __init__(self, one_site, gev, cdf, qua):
        self.one_site = one_site
        self.gev = gev
        self.cdf = cdf
        self.qua = qua

    @classmethod
    def one_site(self, df, site, element):
        # transform data to matrix style
        if len(df[df['SiteId'] == site]) != 0:
            df_one_site = df[df['SiteId'] == site][['Year', element]].pivot_table(values=[element], index=['Year'], margins=True)
            df_one_site = df_one_site.iloc[:-1]
            v0 = np.array(df_one_site)
            return v0
        else:
            return '999999'

    @classmethod
    def gev(self, x):
        # 计算广义极值分布的参数
        x = x[~np.isnan(x)]
        if np.sum(x) == 0.0:
            return np.array([7.15350690e-07, 5.15304206e-06, -9.92961972e-01])
        else:
            return lmoments.pelgev(lmoments.samlmu(x))

    @classmethod
    def cdf(self, x, thres):
        # 根据阈值，计算重现期年数或概率
        probs = []
        for t in thres:
            prob = lmoments.cdfgev(t, x)
            probs.append(prob)
        return probs

    @classmethod
    def qua(self, x, years):
        # 根据重现期反推阈值
        thres = []
        for y in years:
            thre = lmoments.quagev(y, x)
            thres.append(thre)
        return thres


# 返回每个月的累计降水量值，以及月平均值
def acc_monthly(data, element, rp_lst, site_id, city_name, gev_fist=GEV):
    acc = data.drop(['Day'], axis=1).groupby(['SiteId', 'Year', 'Month'], as_index=0).sum()
    avg = acc.drop(['Year'], axis=1).groupby(['SiteId', 'Month'], as_index=0).mean()

    # 计算重现期，并输出结果
    mat = gev_fist.one_site(acc, site_id, element)
    rpYear = 1-1.0/np.array(rp_lst)
    params = np.apply_along_axis(gev_fist.gev, 1, mat)
    rp = np.apply_along_axis(gev_fist.qua, 1, params, rpYear)
    res = pd.DataFrame([rp], columns=rp_count(year, s_mat))
    res.insert(0, 'Average', avg[avg['SiteId'] == site_id][element].values)
    res.insert(0, 'Month', range(6, 11))
    res.insert(0, 'City', city_name)
    return res


def acc_daily(df, element, rp_lst, site_id, city_name, gev_fist=GEV):
    group = df.drop(['Month', 'Day'], axis=1).groupby(['SiteId', 'Year'], as_index=0).sum()
    # 计算重现期，并输出结果
    mat = GEV.one_site(group, site_id, element)
    rpYear = 1-1.0/np.array(rp_lst)
    params = GEV.gev(mat)
    rp = GEV.qua(params, rpYear)
    res = pd.DataFrame([rp], columns=rp_count(year, s_mat))
    res.insert(0, 'City', city_name)
    return res


# 生成赔付率为1的重现期年数表
def rp_count(x1, mat):
    def rate_count(x1, x):
        rp = np.array([x1, x, x * 2, x * 5, x * 8])
        return sum(1.0 / rp * mat)
    sign = 1
    rpYears = []
    for i in range(30, 500, 1):
        n = float(i)/10
        if abs(rate_count(x1, n)-1) < sign:
            sign = abs(rate_count(x1, n)-1)
            rpYears = [x1, n, n*2, n*5]
    return rpYears

sl = pd.read_excel(r'D:\project\Bussiness\AnXin\flood\siteListAll.xlsx')

while True:
    print ('\n    \*---------- 保费测算工具v0.1 ------------*\\\n'.decode('utf-8').encode('gbk'))
    II = InfoInput()
    # 1.输入简单赔付率
    s_mat = II.input_spr()
    # 2.输入最低重现年数
    year = II.input_year()
    # 3.输入城市
    city,site = II.input_city(sl)
    # 4.输入起始终止时间
    start, end = II.input_time()
    # 5.输入要素
    elements = II.input_ele()
    ele = elements.split(',')[-1]
    # 6.获取数据
    df = data_export(elements, site, start, end)
    # 7.计算赔付率
    rate = sum(1.0/np.array(rp_count(year, s_mat)) * s_mat)
    # 8.计算最终结果
    result = acc_daily(df, element=ele, rp_lst=rp_count(year, s_mat), site_id=site, city_name=city)

    # 简单赔付输出准备
    e1, e2, e3, e4, e5 = (s_mat*100).tolist()
    print ('\n')
    print (result)
    print ('\n 站点号为：%.0f'.decode('utf-8').encode('gbk') % site)
    print (' --------------------------------------')
    print (' 赔付率为：%.2f'.decode('utf-8').encode('gbk') % rate)
    print (' --------------------------------------')
    print (' 简单赔付率矩阵为：%0.f%%，%0.f%%，%0.f%%，%0.f%%，%0.f%%'.decode('utf-8').encode('gbk')%(e1, e2, e3, e4, e5))
    print (' --------------------------------------')
    op = raw_input(' 输入回车继续，输入Q退出程序：'.decode('utf-8').encode('gbk'))
    if op == 'Q':
        break
    else:
        continue
