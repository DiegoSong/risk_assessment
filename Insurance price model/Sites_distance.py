import pandas as pd
import math
import copy


# 经纬度计算距离公式
def distance(lat1,lng1,lat2,lng2):
    ER = 6378.137
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    a = lat1 - lat2
    b = math.radians(lng1) - math.radians(lng2)
    s = 2 * math.asin(math.sqrt(math.pow(math.sin(a/2),2)+math.cos(lat1)*math.cos(lat2)*math.pow(math.sin(b/2),2)))
    s = s * ER
    return s


def distance_and_hight():
    Siteslist = pd.read_csv(r'Siteslist.csv')
    Siteslistcopy = copy.deepcopy(Siteslist)

    mdlist1 = []
    mdlist2 = []
    mdlist3 = []

    s = 1
    for lat1, lng1, hight1 in zip(Siteslist['Lat'], Siteslist['Lng'], Siteslist['Hight']):
        df = pd.DataFrame()
        temp = []
        for id, lat2, lng2, hight2 in zip(Siteslistcopy['Siteid'], Siteslistcopy['Lat'], Siteslistcopy['Lng'], Siteslistcopy['Hight']):
            d = distance(lat1, lng1, lat2, lng2)
            h = abs(hight1 - hight2)
            if (d<282) & (h<100):
                temp.append([id,d,h])
            else:
                temp.append([99999,99999,99999])
        df = pd.DataFrame(temp)
        df = df.sort_values(1)
        df.reset_index(drop=True)
        mdlist1.append([df.iloc[1, 0], df.iloc[1, 1], df.iloc[1, 2]])
        mdlist2.append([df.iloc[2, 0], df.iloc[2, 1], df.iloc[2, 2]])
        mdlist3.append([df.iloc[3, 0], df.iloc[3, 1], df.iloc[3, 2]])
        print(s)
        s += 1
    mddf1 = pd.DataFrame(mdlist1, columns=['Clostsite1','MinD1','Height1'])
    mddf2 = pd.DataFrame(mdlist2, columns=['Clostsite2','MinD2','Height2'])
    mddf3 = pd.DataFrame(mdlist3, columns=['Clostsite3','MinD3','Height3'])
    newlist = pd.concat([Siteslist['Siteid'], mddf1, mddf2, mddf3], axis=1)
    newlist.to_csv(r'newlist.csv', index=False)

def distanceonly():
    Siteslist = pd.read_csv(r'Siteslist.csv')
    Siteslistcopy = copy.deepcopy(Siteslist)

    mdlist1 = []
    mdlist2 = []
    mdlist3 = []

    s = 1
    for lat1, lng1, hight1 in zip(Siteslist['Lat'], Siteslist['Lng'], Siteslist['Hight']):
        df = pd.DataFrame()
        temp = []
        for id, lat2, lng2, hight2 in zip(Siteslistcopy['Siteid'], Siteslistcopy['Lat'], Siteslistcopy['Lng'], Siteslistcopy['Hight']):
            d = distance(lat1, lng1, lat2, lng2)
            h = abs(hight1 - hight2)
            if d<500:
                temp.append([id,d,h])
            else:temp.append([99999,99999,99999])
        df = pd.DataFrame(temp)
        df = df.sort_values(1)
        df.reset_index(drop=True)
        mdlist1.append([df.iloc[1, 0], df.iloc[1, 1]])
        mdlist2.append([df.iloc[2, 0], df.iloc[2, 1]])
        mdlist3.append([df.iloc[3, 0], df.iloc[3, 1]])
        print(s)
        s += 1
    mddf1 = pd.DataFrame(mdlist1, columns=['Clostsite1','MinD1'])
    mddf2 = pd.DataFrame(mdlist2, columns=['Clostsite2','MinD2'])
    mddf3 = pd.DataFrame(mdlist3, columns=['Clostsite3','MinD3'])

    newlist = pd.concat([Siteslist['Siteid'], mddf1, mddf2, mddf3], axis=1)

    newlist.to_csv(r'newlist_distonly.csv', index=False)
distanceonly()
