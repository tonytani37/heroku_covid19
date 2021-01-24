import streamlit as st
import pandas as pd 
import numpy as np 
import plotly.express as px
import json
import requests
import matplotlib.pyplot as plt
import japanize_matplotlib

json_name = 'summary.json'

url='https://raw.githubusercontent.com/reustle/covid19japan-data/master/docs/summary/latest.json'

try:
    r = requests.get(url)
    with open(json_name, mode='w') as f:
        f.write(r.text)
except requests.exceptions.RequestException as err:
    print(err)

f = open(json_name,'r')
summary_json = json.load(f)

collist = [
        'date',
        "confirmed",
        "recoveredCumulative",
        "deceasedCumulative",
        "criticalCumulative",
        "testedCumulative",
        "confirmedCumulative",
        "confirmedAvg3d",
        "confirmedCumulativeAvg3d",
        "confirmedAvg7d",
        "confirmedCumulativeAvg7d"
        ]

datalist = [
            [row['date'],
             row['confirmed'],
             row['recoveredCumulative'],
             row['deceasedCumulative'],
             row['criticalCumulative'],
             row['testedCumulative'],
             row['confirmedCumulative'],
             row['confirmedAvg3d'],
             row['confirmedCumulativeAvg3d'],
             row['confirmedAvg7d'],
             row['confirmedCumulativeAvg7d']
             ] 
            for row in summary_json['daily']
            ]

df = pd.DataFrame(datalist,columns=collist)

df.to_csv('summary.csv')

update = summary_json['updated'][:10]

df = pd.read_csv('summary.csv')
df = df.drop(0)

df_a = df[['date','confirmed','confirmedAvg7d']].copy()
df_ｃ = df['confirmedAvg7d'].copy()

df_t = df['testedCumulative'].diff()

df_ta = list(df_t.rolling(7).mean())
df_a['検査数'] = df_t
df_a['検査数移動平均'] = df_ta

df_a = df_a.rename(
    columns={'date':'日付','confirmed':"感染者数",'confirmedAvg7d':'感染者数移動平均'})

df_d = pd.to_datetime(df_a['日付'])
df_a = df_a.drop('日付',axis=1)
df_a = df_a.fillna(0).astype(int)
df_a['日付'] = df_d


fig, ax1 = plt.subplots(figsize=(12,8))
ax2 = ax1.twinx()
# ax1.bar(df_a['日付'].tail(240),df_a['感染者数'].tail(240),label='日次感染者数',color='lightgray')
ax1.plot(df_a['日付'].tail(240),df_a['感染者数移動平均'].tail(240),label='感染者数移動平均',color='red')
ax2.plot(df_a['日付'].tail(240),df_a['検査数移動平均'].tail(240),label='検査数移動平均',color='green')

title = "国内感染者数推移（日毎 移動平均)  {}".format(update)
ax1.set_title(title)

ax1.set_xlabel('日付')
ax1.set_ylabel("7日平均感染者数")
ax2.set_ylabel("7日平均検査者数")

hd1, lb1 = ax1.get_legend_handles_labels()
hd2, lb2 = ax2.get_legend_handles_labels()
# 凡例をまとめて出力する
ax1.legend(hd1 + hd2, lb1 + lb2, loc='upper left')
# d_list = [a for a in range(0,240,30)]
# d_list.append(239)
# plt.xticks(d_list)
plt.grid(True)

st.title('COVID-19 全国感染者情報')
st.write('このサイトはStreamlitで作成しています')

st.pyplot(fig)

st.write(
    px.bar(df_a.tail(240),x='日付',y="感染者数",title='感染者数')
)
st.write(
    px.bar(df_a.tail(240),x='日付',y="検査数",title='検査数')
)
# f = open(json_name,'r')
# summary_json = json.load(f)

# data_n = [row['name_ja'] for row in summary_json['prefectures']] #都道府県名
# data_l = [row['dailyConfirmedCount'] for row in summary_json['prefectures']] #感染者数
# data_d = [row['dailyDeceasedCount'] for row in summary_json['prefectures']] #死亡者数

# df_pre = pd.DataFrame(data_d)

# st.write(
#     px.line(df_pre)
# )

# st.dataframe(df_pre)


st.write('COVID-19感染者関連データ')
st.dataframe(df_a.style.highlight_max(axis=0),width=900,height=400)

st.write(
    'https://raw.githubusercontent.com/reustle/covid19japan-data/master/docs/summary/latest.json'
    )
