### 保险产品设计
一款保险产品上线申报需要可研报告及费率表，以上是与保险公司合作设计气象保险产品的实例，费率表或可研报告中所需的数据、算法支持。
### 概览
程序名 | 描述
--- | ---
High_temperature_insurance_probability.py | 2015年上线的XX高温险产品，背后的费率精算方法
Preciption_insurance_probability.py | 保险公司给定保额保费比，给出每周最多赔偿1次，按月售卖的降雨险方案
Reappearing_period.py | 基于广义极值分布拟合的重现期模型
Tea_insurance_price_backtrack.py | 某茶叶低温险精算逻辑
hourly_to_daily.py | 时间序列数据重采样 
Sites_distance.py | 经纬度计算距离公式
### 数据库表结构
![image](https://thumbnail0.baidupcs.com/thumbnail/3c7bfab40e586520ac40ab53114a2436?fid=3926101868-250528-151919967924414&time=1490338800&rt=sh&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-EUbLr%2FH6huUckeaaF%2FEMBZfX4gg%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=1916355484103896592&dp-callid=0&size=c710_u400&quality=100)

序号 |字段表
--- | ---
1 | SiteId
2| Day
3|PressureAverage
4|PressureMax
5|PressureMin
6|TemperatureAverage
7|TemperatureMax
8|TemperatureMin
9|RelativeHumidityAverage
10|RelativeHumidityMin
11|Precipitation20_8
12|Precipitation8_20
13|Precipitation20_20
14|EvaporationSmall
15|EvaporationLarge
16|WindSpeedAverage
17|WindSpeedMax
18|WindSpeedMaxDirection
19|WindSpeedExtreme
20|WindSpeedExtremeDirection
21|SunshineHour
22|SurfaceTemperatureAverage
23|SurfaceTemperatureMax
24|SurfaceTemperatureMin

