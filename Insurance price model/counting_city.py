import pymysql
import pandas as pd

def main():
    mon = ['06', '07', '08', '09']
    Date = chartname(mon)
    #Sitelist = open(r'siteslist_city.txt').read()
    Elements = ['SiteId,Day,TemperatureMax']
    Sitelist = '54511,58367'
    df = data_export(Date, Elements, Sitelist)
    df_result = data_stats(df)
    df_result.to_csv(r'D:\project\Bussiness\TaiKang\result.csv',index=0)


def data_export(Date,Elements,Sitelist):
    # 最高温度数据提取
    conn = pymysql.connect(host='###', user='###', passwd='###', db='weatherhistory')
    cur = conn.cursor()
    df = pd.DataFrame()
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


def data_stats(df):
    # 统计每年的高温天数，以历史统计频率作为风险概率
    df['TemperatureMax'] = df['TemperatureMax'].replace(32766, 0)
    df['TemperatureMax'] = df['TemperatureMax'] / 10
    dfe = pd.read_excel(r'D:\project\Bussiness\TaiKang\siteslist_city.xlsx')
    dfe = dfe.drop(['气象站名'], axis=1)
    dfn = pd.merge(df, dfe, how='left', left_on=['SiteId'], right_on=['气象站号'])
    dfn = dfn.groupby(['城市', 'Year', 'Month', 'Day'], as_index=False).max().drop(['SiteId', '气象站号'], axis=1)
    r1 = (dfn['TemperatureMax'] >= 35) * 1
    r2 = (dfn['TemperatureMax'] >= 36) * 1
    dfn['degree35'] = r1
    dfn['degree36'] = r2
    df_append = dfn.groupby(['城市', 'Month', 'Day'], as_index=False).sum().drop(['TemperatureMax'], axis=1)
    df_append.iloc[:, 3:] = df_append.iloc[:, 3:] / 30
    df_append.columns = ['城市', '月', '日', '35℃及以上', '36℃及以上']
    # df_append.to_csv(r'data.csv', index=False)
    return df_append

main()
