# coding=utf-8
import pandas as pd
from fbprophet import Prophet
import matplotlib.pyplot as plt


# 利用prophet预测时间序列
# 传入参数：l，类型为list，为时间序列的值
# 返回参数：res，类型为float，默认保留3位小数，为第一个预测值
# 预测窗口长度默认为传入l长度的十分之一
# 预测图片保存在 time_series_detector/output 目录下
def predict(l):
    stamp = pd.date_range(start='2020-01-01', periods=len(l), freq='T')
    lists = []
    for index in range(len(l)):
        lists.append([])
        lists[index].append(stamp[index])
        lists[index].append(l[index])

    df = pd.DataFrame(lists)
    df.rename(columns={0: "ds", 1: "y"}, inplace=True)
    # print(df.head())

    # 拟合模型
    m = Prophet()
    m.fit(df)

    # 构建待预测日期数据框，periods代表新增窗口长度，freq代表频率，M是月，D是天，T是分钟
    future = m.make_future_dataframe(periods=int(len(l) / 10), freq='T')
    print(future)

    # 预测数据集
    forecast = m.predict(future)
    fc = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    print(fc.tail())
    res = fc.loc[len(l), "yhat"]

    # 展示并保存预测结果
    m.plot(forecast)
    plt.savefig('../output/p1')
    plt.show()

    # 预测的成分分析绘图，展示预测中的趋势、周效应和年度效应
    m.plot_components(forecast)
    plt.savefig('../output/trend1')
    plt.show()

    return round(res, 3)
