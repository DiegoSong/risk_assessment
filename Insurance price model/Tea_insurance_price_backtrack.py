import pandas as pd
import pymysql

'''
根据保险公司给出的现有保险产品价格矩阵，反算每年总的赔付金额

'''


def data_export(Date, Elements, Sitelist):
    # 从数据库中提取最低温度数据
    conn = pymysql.connect(host='###', user='###', passwd='###', db='weatherhistory')
    cur = conn.cursor()
    df=pd.DataFrame()
    for i in Date:
        cur.execute("SELECT %s FROM ViewHistory%s where Siteid in (%s)"%(Elements[0],i,Sitelist))
        r = cur.fetchall()
        rdf = pd.DataFrame(list(r))
        rdf = rdf.replace(32700, 0)
        year = pd.DataFrame([i[:4]]*len(r))
        month = pd.DataFrame([i[4:]]*len(r))
        rdf = pd.concat([rdf, year, month], axis=1)
        df = df.append(rdf)
        print(i)
    df.columns = Elements[0].split(',')+['Year', 'Month']
    y = df.pop('Year')
    m = df.pop('Month')
    df.insert(1,'Year', y)
    df.insert(2,'Month', m)
    return df


def chartname(mon):
    # 生成数据表名中的年月部分
    Date=[]
    for year in range(1987, 2017, 1):
        for m in mon:
            date = str(year)+str(m)
            Date.append(date)
    return Date


def fit_price(period, data, prices):
    data = data.reset_index(drop=True)
    price_fin = pd.Series(([0]*len(data)))
    for i in thres_range:
        price_tmp = data['%s Degree'% i] * int(prices[prices['Period'] == period]['%s Degree'% i])
        price_fin = price_fin + price_tmp
    data['price'] = price_fin
    df_group1 = data[['SiteId','Year','price']]
    df_group1 = df_group1.groupby(['SiteId','Year'], as_index=False).sum()
    df_group2 = df_group1[['Year','price']].groupby(['Year'], as_index=False).mean()
    return df_group2


def main():
    # 气象站点编号、字段名
    Sitelist = '58341,58344,58354,58252,58346'
    Elements = ['SiteId,Day,TemperatureMin']
    mon = ['03', '04']
    Date = chartname(mon)
    df = data_export(Date, Elements, Sitelist)
    # 计算几个阈值区间
    thres_range = range(-8, 3)
    for i in thres_range:
        df['%s Degree' % i] = ((df['TemperatureMin'] <= i * 10) & (df['TemperatureMin'] > (i - 1) * 10)) * 1

    data1 = df[(df['Month'] == '03') & (df['Day'] <= 10)]
    data2 = df[(df['Month'] == '03') & (df['Day'] <= 20) & (df['Day'] >= 11)]
    data3 = df[(df['Month'] == '03') & (df['Day'] <= 31) & (df['Day'] >= 21)]
    data4 = df[(df['Month'] == '04') & (df['Day'] <= 10)]
    data5 = df[(df['Month'] == '04') & (df['Day'] <= 20) & (df['Day'] >= 11)]
    data6 = df[(df['Month'] == '04') & (df['Day'] <= 30) & (df['Day'] >= 21)]
    # 加载保险产品价格矩阵
    prices = pd.read_csv(r'Tea_insurance_price.csv')
    df_tmp1 = fit_price('p1', data1, prices)
    df_tmp2 = fit_price('p2', data2, prices)
    df_tmp3 = fit_price('p3', data3, prices)
    df_tmp4 = fit_price('p4', data4, prices)
    df_tmp5 = fit_price('p5', data5, prices)
    df_tmp6 = fit_price('p6', data6, prices)
    df_res = pd.concat([df_tmp1, df_tmp2['price'],df_tmp3['price'],df_tmp4['price'],df_tmp5['price'],df_tmp6['price']], axis=1)
    df_res.columns = ['Year','price1','price2','price3','price4','price5','price6']
    df_res['avg'] = (df_res['price1']+df_res['price2']+df_res['price3']+df_res['price4']+df_res['price5']+df_res['price6'])
    df_res['avg'] = df_res['avg'].apply(lambda x: round(x, 0))
    return df_res

main().to_csv(r'result\backtrack.csv', index=False)

