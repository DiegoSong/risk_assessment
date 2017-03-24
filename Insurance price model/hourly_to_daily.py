import pymysql
import pandas as pd

'''
数据时间尺度转换, 将小时频率观测数据，
处理成20时-20时的日值观测数据，
不同要素采用不同的采样方式。
'''

def data_export(Sitelist, sql):
    conn = pymysql.connect(host='###', user='###', passwd='###', db='obs2hour')
    cur = conn.cursor()
    df = pd.DataFrame()
    cur.execute(sql.format(sites=Sitelist))
    r = cur.fetchall()
    rdf = pd.DataFrame(list(r))
    rdf = rdf.replace(32700, 0)
    df = df.append(rdf)
    df.columns = ['SiteId', 'date', 'prec20_20', 'tempAvg', 'tempMin']
    df['date'] = pd.to_datetime(df['date'])
    df.iloc[:, 2:] = df.iloc[:, 2:] * 10
    return df


def form(df):
    tmp = []
    for i in range(len(df)):
        a = df.iloc[i, :]
        year = a[1].year
        month = a[1].month
        day = a[1].day
        tmp.append([a[0], year, month, day, round(a[2],0), round(a[3],0), round(a[4],0)])
    dff = pd.DataFrame(tmp, columns=['SiteId', 'year', 'month', 'day', 'prec20_20', 'tempAvg', 'tempMin'])
    return dff

sql = '''
    SELECT
        STATION_ID,
        DATE_ADD(DataTime, INTERVAL 4 HOUR) as date,
        sum(if (PRE_1H BETWEEN 0 and 500,PRE_1H,0)) AS PREC20_20,
        avg(if (TEM BETWEEN -70 and 70,TEM,0)) AS Tavg,
        MIN(if (TEM_MIN BETWEEN -70 and 70,TEM_MIN,0)) AS Tmin
    FROM
    (
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201512
        WHERE STATION_ID in ({sites})
        UNION
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201601
        WHERE STATION_ID in ({sites})
        UNION
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201601
        WHERE STATION_ID in ({sites})
        UNION
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201602
        WHERE STATION_ID in ({sites})
        UNION
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201603
        WHERE STATION_ID in ({sites})
        UNION
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201604
        WHERE STATION_ID in ({sites})
        UNION
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201605
        WHERE STATION_ID in ({sites})
        UNION
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201606
        WHERE STATION_ID in ({sites})
        UNION
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201607
        WHERE STATION_ID in ({sites})
        UNION
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201608
        WHERE STATION_ID in ({sites})
        UNION
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201609
        WHERE STATION_ID in ({sites})
        UNION
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201610
        WHERE STATION_ID in ({sites})
        UNION
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201611
        WHERE STATION_ID in ({sites})
        UNION
        SELECT STATION_ID,DataTime,PRE_1H,TEM,TEM_MIN from
        observe_hour.obs_hour201612
        WHERE STATION_ID in ({sites})
    ) a
    GROUP BY
        STATION_ID,DATE(date)
    '''

def main():
    s_nei = '54511,58367,57131,59287'
    df2 = data_export(s_nei, sql)
    df_nei = form(df2)
    df_nei = df_nei[df_nei['year'] == 2016]
    df_nei.to_csv(r'nei2016.csv', index=0)
