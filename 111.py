import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



# %%
df = pd.read_csv('ev_charging_patterns.csv')
df.head(10)
# %%
df.info()
# %%
# 转换为时间变量
df['Charging Start Time'] = pd.to_datetime(df['Charging Start Time'], errors='coerce')
df['Charging End Time'] = pd.to_datetime(df['Charging End Time'], errors='coerce')

# 转化为类型变量减小内存占用(净整没用的
categorical_columns = ['User Type', 'Vehicle Model', 'Charging Station Location', 'Time of Day', 'Day of Week',
                       'Charger Type']
for column in categorical_columns:
    df[column] = df[column].astype('category')

# %%
# 删除含空值的行，重复行
df = df.dropna()
df = df.drop_duplicates()

# 把电越充越少坏东西的删掉
df = df.drop(df[df['State of Charge (End %)'] < df['State of Charge (Start %)']].index)

# 把充满了的删掉（因为会影响我们不知道他实际充电时间了（比划
df = df[df['State of Charge (End %)'] <= 99]

# %%
# 构造新特征充电持续时间，不知道有啥用先搞了再说
df['Charging Duration_Cate'] = pd.cut(df['Charging Duration (hours)'],
                                      bins=[0, 1, 3, 6, np.inf],
                                      labels=['Short (<1 hr)', 'Medium (1-3 hrs)', 'Long (3-6 hrs)',
                                              'Very Long (>6 hrs)'])

# Display count of different charging duration categories
()
# %%
# 用实际数据计算出实际的充电效率Charging Efficiency，啊这个啊很重要很重要要考的啊
df['Charging Efficiency'] = (((df['State of Charge (End %)'] - df['State of Charge (Start %)']) / 100) * df[
    'Battery Capacity (kWh)']) / df['Charging Duration (hours)']

# 与原表中的理论值Charging Rate (kW)作比较
df['Loss'] = df['Charging Rate (kW)'] - df['Charging Efficiency']

# %%
# Remove obvious outliers in Charging Efficiency 去除极端的异常值
q1 = df['Charging Efficiency'].quantile(0.25)
q3 = df['Charging Efficiency'].quantile(0.75)
lower_bound = q1 - 1.5 * (q3 - q1)
upper_bound = q3 + 1.5 * (q3 - q1)
df = df[(df['Charging Efficiency'] >= lower_bound) & (df['Charging Efficiency'] <= upper_bound)]

# 把右侧Charging Rate太大的删掉
df = df[df['Charging Rate (kW)'] <= df['Charging Rate (kW)'].quantile(0.95)]




def draw_scatter(X, Y, label):
    unique_categories = df[[label]].drop_duplicates()
    color_name = "Paired"
    select = (0, 3, 5, 7, 9)
    color = plt.get_cmap(color_name)(select)

    for i in range(0, len(unique_categories)):
        data = df[(df[label] == unique_categories.iloc[i, 0])]
        plt.scatter(data[X], data[Y], c=color[i], label=unique_categories.iloc[i, 0])
    plt.legend(title=label, loc="upper right")
    plt.xlabel(X)
    plt.ylabel(Y)
    plt.title(X + " with " + Y)
    plt.savefig(X+label+".png")
    plt.show()

list = ['Charging Duration (hours)', 'Time of Day', 'State of Charge (Start %)', 'State of Charge (End %)', 'Temperature (°C)', 'Vehicle Age (years)']
list2 = ["User Type", "Vehicle Model"]



for row in list:
    for label in list2:
        draw_scatter(row, "Charging Efficiency", label)
