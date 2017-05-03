# coding:utf-8
import numpy as np
import pandas as pd
import scipy.stats as stats
from matplotlib import pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

# 确定评估结果数据的置信区间
data = pd.read_excel(r'D:\project\Bussiness\AnXin\Typhoon\Final_data.xlsx').values
expo = stats.expon.fit(data)
x = np.linspace(0.25, 10, 9500)
y = stats.expon.pdf(x, expo[0], expo[1])
fig, ax = plt.subplots(1, 1)
ax.plot(x, y, linewidth=3, label=u'拟合指数分布曲线')
ax.hist(data,normed=1, bins=30, label=u'赔付率数据')
ax.legend(loc='best', frameon=False)
plt.show()

interval_90 = stats.expon.interval(0.9, expo[0], expo[1])
interval_95 = stats.expon.interval(0.95, expo[0], expo[1])

