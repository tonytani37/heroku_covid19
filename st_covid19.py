import streamlit as st
import pandas as pd 
import numpy as np 
import plotly.express as px
import json
import requests
import matplotlib.pyplot as plt
import japanize_matplotlib
from datetime import datetime, timedelta, timezone

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

df_a = df[['date','confirmed','confirmedAvg7d',"criticalCumulative"]].copy() #dataframeはcopyしないとワーニングが出る
df_ｃ = df['confirmedAvg7d'].copy() #dataframeはcopyしないとワーニングが出る

df_t = df['testedCumulative'].diff()

df_ta = list(df_t.rolling(7).mean())
df_a['検査数'] = df_t
df_a['検査数移動平均'] = df_ta

df_a = df_a.rename(
    # columns={'confirmed':"感染者数",'confirmedAvg7d':'感染者数移動平均'})
    columns={'date':'日付','confirmed':"感染者数",'confirmedAvg7d':'感染者数移動平均',"criticalCumulative":'重症者数'}
    )

df_bd = df_a['日付'].copy()
df_d = pd.to_datetime(df_a['日付']).copy()
df_a = df_a.drop('日付',axis=1)
df_a = df_a.fillna(0).astype(int)
df_show = df_a.copy()
df_show['日付'] = df_bd
df_a['日付'] = df_d
# df_df = df_d.iloc[0]

days = 300 #グラフ化する日数指定

fig, ax1 = plt.subplots(figsize=(12,8))
ax2 = ax1.twinx()
ax1.bar(df_a['日付'].tail(days),df_a['感染者数'].tail(days),label='日次感染者数',color='lightgray')
ax1.plot(df_a['日付'].tail(days),df_a['感染者数移動平均'].tail(days),label='感染者数移動平均',color='red',linewidth=2)
ax2.plot(df_a['日付'].tail(days),df_a['検査数移動平均'].tail(days),label='検査数移動平均',color='green',linewidth=2)

if datetime(2020,4,7) > min(df_a['日付'].tail(days)):
    plt.axvline(x=datetime(2020,4,7), color='red', ls='--')
if datetime(2020,4,21) > min(df_a['日付'].tail(days)):
    plt.axvline(x=datetime(2020,4,21), color='blue', ls='--')
if datetime(2020,10,1) > min(df_a['日付'].tail(days)):
    plt.axvline(x=datetime(2020,10,1), color='gray', ls='--')
if datetime(2020,7,22) > min(df_a['日付'].tail(days)):
    plt.axvline(x=datetime(2020,7,22), color='gray', ls='--')
if datetime(2021,1,8) > min(df_a['日付'].tail(days)):
    plt.axvline(x=datetime(2021,1,8), color='red', ls='--')
if datetime(2021,1,22) > min(df_a['日付'].tail(days)):
    plt.axvline(x=datetime(2021,1,22), color='blue', ls='--')
    
title = "国内感染者数推移（日毎 移動平均)  {}".format(update)
ax1.set_title(title)

ax1.set_xlabel('日付')
ax1.set_ylabel("7日平均感染者数（人）")
ax2.set_ylabel("7日平均検査者数（件）")

hd1, lb1 = ax1.get_legend_handles_labels()
hd2, lb2 = ax2.get_legend_handles_labels()
# 凡例をまとめて出力する
ax1.legend(hd1 + hd2, lb1 + lb2, loc='upper left')
plt.grid(True)

# df_cr = df[['date',"criticalCumulative"]]

# df_b = df_cr.rename(
#     columns={'date':'日付',"criticalCumulative":'重症者数'})

df_d = pd.to_datetime(df_a['日付'])
df_a = df_a.drop('日付',axis=1)
df_a = df_a.fillna(0).astype(int)
df_a['日付'] = df_d

fig3, ax1 = plt.subplots(figsize=(12,8))

ax1.plot(df_a['日付'].tail(days),df_a['重症者数'].tail(days),label='重症者数',color='green')

if datetime(2020,4,7) > min(df_a['日付'].tail(days)):
    plt.axvline(x=datetime(2020,4,7), color='red', ls='--')
if datetime(2020,4,21) > min(df_a['日付'].tail(days)):
    plt.axvline(x=datetime(2020,4,21), color='blue', ls='--')
if datetime(2020,10,1) > min(df_a['日付'].tail(days)):
    plt.axvline(x=datetime(2020,10,1), color='gray', ls='--')
if datetime(2020,7,22) > min(df_a['日付'].tail(days)):
    plt.axvline(x=datetime(2020,7,22), color='gray', ls='--')
if datetime(2021,1,8) > min(df_a['日付'].tail(days)):
    plt.axvline(x=datetime(2021,1,8), color='red', ls='--')
if datetime(2021,1,22) > min(df_a['日付'].tail(days)):
    plt.axvline(x=datetime(2021,1,22), color='blue', ls='--')

title = "国内重傷者数推移 {}".format(update)
ax1.set_title(title)

ax1.set_xlabel('日付')
ax1.set_ylabel("重傷者（人）")

ax1.legend()
plt.grid(True)

"""
# COVID-19 全国感染者情報
### このサイトはStreamlitで作成したものをHerokuで公開しています
#### matplotlib
"""

"""
### 国内感染者数（移動平均）
"""

st.pyplot(fig)

"""
### 国内重症者累計推移
"""

st.pyplot(fig3)

"""
### COVID-19感染者関連データ
"""

st.dataframe(df_show[['日付','感染者数','検査数','重症者数','感染者数移動平均','検査数移動平均']].style.highlight_max(axis=0),height=400)

st.write(
    'data: https://raw.githubusercontent.com/reustle/covid19japan-data/master/docs/summary/latest.json'
    )

data_n = [row['name_ja'] for row in summary_json['prefectures']] #都道府県名
data_l = [row['dailyConfirmedCount'] for row in summary_json['prefectures']] #感染者数
data_d = [row['dailyDeceasedCount'] for row in summary_json['prefectures']] #死亡者数

import datetime as dt

s_day = '2020-01-08' #開始日
# s_day = '2020-01-18' #開始日

# JST = timezone(timedelta(hours=+9), 'JST')
# date_time = dt.datetime.now(JST)
date_time = pd.to_datetime(df_d.iloc[-1])
today = date_time.strftime("%Y-%m-%d")
date_index = pd.date_range(s_day , today, freq="d")
date_idx = ["{0:%Y-%m-%d}".format(row) for row in date_index]
date_idx = date_idx[-days:]
df_date = pd.DataFrame(date_idx,columns=['日付'])

df_date = df_date['日付']
df_n = pd.DataFrame(data_n)

# 内容表記でスライスは何故かダメみたい
data_ls = []
for row in data_l:
    data_ls.append(row[-days:])

df_l = pd.DataFrame(data_ls,columns=df_date)
df_l['name_ja'] = df_n.tail(days).copy()
# df_l = df_l.set_index('name_ja')
df_sum = df_l.sum(axis=1)
df_l['sum'] = df_sum
df_l = df_l.fillna(0)

# 内容表記でスライスは何故かダメみたい
data_ds = []
for row in data_d:
    data_ds.append(row[-days:])

df_d = pd.DataFrame(data_ds,columns=df_date)
df_d['name_ja'] = df_n.tail(days).copy()
# df_d = df_d.set_index('name_ja')
df_sum = df_d.sum(axis=1)
df_d['sum'] = df_sum
df_d = df_d.fillna(0)


marker_s = [
            "p", 
            "^", 
            "1", 
            "8", 
            "s", 
            "p", 
            "^", 
            "1", 
            "8", 
            "s", 
            "p", 
            "^", 
            "1", 
            "8", 
            "s",
            "p", 
            "^", 
            "1", 
            "8", 
            "s",
            "p", 
            "^", 
            "1", 
            "8", 
            "s",
            "p", 
            "^", 
            "1", 
            "8", 
            "s",
            "p", 
            "^", 
            "1", 
            "8", 
            "s",
            "p", 
            "^", 
            "1", 
            "8", 
            "s",
            "p", 
            "^", 
            "1", 
            "8", 
            "s"
            ]

# 都道府県別死亡者数

df = df_d[df_d['sum'] > 300]
df = df.head(10)
idx = len(df)

df_name = df_d['name_ja']
df_c = df.drop(['name_ja','sum'],axis=1)
df_col = df_c.columns.values

# days = 300
day_m = 0 - days
df_col = df_col[day_m:]
df_col = pd.to_datetime(df_col).copy()

# df_c = df_c.astype(int).copy()

# df_c.to_csv('json/test.csv')

fig1, ax1 = plt.subplots(figsize=(12,8))

for i in range(idx):
    if not df_name[i] == 'ダイヤモンド・プリンセス' and not df_name[i] == '長崎のクルーズ船' and not df_name[i] == '空港検疫':
        df_1 = df_c.iloc[i]
        df_2 = df_1.rolling(7).mean()
        df_2 = df_2[day_m:]
        # ax1.plot(df_col,df_2,label=df_name[i],linewidth=2,marker=marker_s[i])
        ax1.plot(df_col,df_2,label=df_name[i],linewidth=2)

plt.grid()
ax1.set_title('都道府県別死亡者数（移動平均） {}'.format(update))
ax1.set_xlabel('日付')
ax1.set_ylabel('死亡者数（人）')
plt.legend(loc='upper left')

# """
# ### 都道府県別死亡者数（移動平均）
# """

# st.pyplot(fig1)


df = df_l[df_l['sum'] > 1000]
df = df.head(7)
idx = len(df)

df_name = df_l['name_ja']
df_l = df.drop(['name_ja','sum'],axis=1)
df_col = df_c.columns.values

# days = 240
day_m = 0 - days
df_col = df_col[day_m:]
df_col = pd.to_datetime(df_col).copy()


fig2, ax1 = plt.subplots(figsize=(12,8))

for i in range(idx):
    if not df_name[i] == 'ダイヤモンド・プリンセス' and not df_name[i] == '長崎のクルーズ船' and not df_name[i] == '空港検疫':
        df_1 = df_l.iloc[i]
        df_2 = df_1.rolling(7).mean()
        df_2 = df_2[day_m:]
        # ax1.plot(df_col,df_2,label=df_name[i],linewidth=2,marker=marker_s[i])
        ax1.plot(df_col,df_2,label=df_name[i],linewidth=2)


# mem_list = [a for a in range(0,day,14)]
# # plt.xticks([0,7,15,22,29])
# plt.xticks(mem_list)

plt.grid()
ax1.set_title('都道府県別感染者数（移動平均） {}'.format(update))
ax1.set_xlabel('日付')
ax1.set_ylabel('感染者数（人）')
plt.legend(loc='upper left')

# """
# ### 都道府県別感染者者数（移動平均）
# """

# st.pyplot(fig2)

# """
# #### plotly
# """

# st.write(
#     px.bar(df_a.tail(240),x='日付',y="感染者数",title='感染者数')
# )
# st.write(
#     px.bar(df_a.tail(240),x='日付',y="検査数",title='検査数')
# )


# st.write(
#     px.line(df_a.tail(days),x='日付',y='重症者累計',title='重症者累計')
# )

"""
### 都道府県別感染者数（移動平均）
"""

st.pyplot(fig2)

"""
### 都道府県別死亡者数（移動平均）
"""

st.pyplot(fig1)



# st.write(
#     'ソース: https://raw.githubusercontent.com/tonytani37/heroku_covid19/master/st_covid19.py'
#     )
