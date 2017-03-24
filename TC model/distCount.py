import math

def distance(lat1,lng1,lat2,lng2):
    # 经纬度计算距离公式
    ER = 6378.137
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    a = lat1 - lat2
    b = math.radians(lng1) - math.radians(lng2)
    s = 2 * math.asin(math.sqrt(math.pow(math.sin(a/2),2)+math.cos(lat1)*math.cos(lat2)*math.pow(math.sin(b/2),2)))
    s = s * ER
    return s

if __name__=='__main__':
    distance()
