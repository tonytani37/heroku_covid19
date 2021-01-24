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
    summary_json = json.loads(r.text)
except requests.exceptions.RequestException as err:
    print(err)

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

update = summary_json['updated'][:10]

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

days = 240 #グラフ化する日数指定

fig, ax1 = plt.subplots(figsize=(12,8))
ax2 = ax1.twinx()
ax1.bar(df_a['日付'].tail(days),df_a['感染者数'].tail(days),label='日次感染者数',color='lightgray')
ax1.plot(df_a['日付'].tail(days),df_a['感染者数移動平均'].tail(days),label='感染者数移動平均',color='red')
ax2.plot(df_a['日付'].tail(days),df_a['検査数移動平均'].tail(days),label='検査数移動平均',color='green')

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

st.write('matplotlib')

st.pyplot(fig)

st.write('plotly')

st.write(
    px.bar(df_a.tail(240),x='日付',y="感染者数",title='感染者数')
)
st.write(
    px.bar(df_a.tail(240),x='日付',y="検査数",title='検査数')
)

st.write('COVID-19感染者関連データ')
st.dataframe(df_a.style.highlight_max(axis=0),width=900,height=400)

st.write(
    'https://raw.githubusercontent.com/reustle/covid19japan-data/master/docs/summary/latest.json'
    )
