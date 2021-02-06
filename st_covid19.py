import streamlit as st
import pandas as pd 
import numpy as np 
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import requests
import matplotlib.pyplot as plt
import japanize_matplotlib
from datetime import datetime, timedelta, timezone

DAYS = 300 #グラフ化する日数指定

# @st.cache(allow_output_mutation=True, suppress_st_warning=True)
@st.cache()
def data_load():
    url='https://raw.githubusercontent.com/reustle/covid19japan-data/master/docs/summary/latest.json'

    try:
        r = requests.get(url)
        summary_json = json.loads(r.text)
        return summary_json
    except requests.exceptions.RequestException as err:
        print(err)
        
#     json_open = open('file\summary.json', 'r')
#     summary_json = json.load(json_open)
#     return summary_json
    
# @st.cache(allow_output_mutation=True, suppress_st_warning=True)  
@st.cache()  
def tokyo_data():
    url='https://raw.githubusercontent.com/tokyo-metropolitan-gov/covid19/development/data/daily_positive_detail.json'

    try:
        r = requests.get(url)
        summary_json = json.loads(r.text)
        return summary_json
    except requests.exceptions.RequestException as err:
        print(err)

#     json_open = open('file/tokyo.json', 'r')
#     summary_json = json.load(json_open)
#     return summary_json

# @st.cache(allow_output_mutation=True, suppress_st_warning=True)   
def line_set(df,DAYS):
    if datetime(2020,4,7) > min(df['日付'].tail(DAYS)):
        plt.axvline(x=datetime(2020,4,7), color='red', ls='--')
    if datetime(2020,4,21) > min(df['日付'].tail(DAYS)):
        plt.axvline(x=datetime(2020,4,21), color='blue', ls='--')
    if datetime(2020,10,1) > min(df['日付'].tail(DAYS)):
        plt.axvline(x=datetime(2020,10,1), color='gray', ls='--')
    if datetime(2020,7,22) > min(df['日付'].tail(DAYS)):
        plt.axvline(x=datetime(2020,7,22), color='gray', ls='--')
    if datetime(2021,1,8) > min(df['日付'].tail(DAYS)):
        plt.axvline(x=datetime(2021,1,8), color='red', ls='--')
    if datetime(2021,1,22) > min(df['日付'].tail(DAYS)):
        plt.axvline(x=datetime(2021,1,22), color='blue', ls='--')

@st.cache(allow_output_mutation=True, suppress_st_warning=True)    
def data_set(summary_json):
# ### 都道府県別感染者数（移動平均）
    datalist = [
                [row['date']
                ] 
                for row in summary_json['daily']
                ]

    df_h = pd.DataFrame(datalist,columns=['日付'])
    df_h = pd.to_datetime(df_h['日付'])
    df_h = df_h[-DAYS:]

    data_n = [str(i+1).zfill(2)+':'+row['name_ja'] for i,row in enumerate(summary_json['prefectures'])] #都道府県名
#     data_n = [str(i+1).zfill(2)+':'+row['name'] for i,row in enumerate(summary_json['prefectures'])] #都道府県名
    data_l = [row['dailyConfirmedCount'] for row in summary_json['prefectures']] #感染者数
    data_d = [row['dailyDeceasedCount'] for row in summary_json['prefectures']] #死亡者数

    data_ls = []
    for row in data_l: # DAYSで指定された日数分だけ抜き出し
        data_ls.append(row[-DAYS:])
    df_l = pd.DataFrame(data_ls,columns=df_h)

    df_s = []
    for row in data_l: #全部合計
        df_s.append(sum(row))

    df_l.insert(0,'都道府県',pd.DataFrame(data_n))
    df_l.insert(1,'合計',pd.DataFrame(df_s))

    ## 都道府県別の感染者合計と直近の感染者数をDataFrameにコピーする ##
    df_total = pd.DataFrame(data_n,columns={'都道府県'})
    df_total['　　感染者計　'] =  pd.DataFrame(df_s)
    if df_l.iloc[:,-1].sum() == 0:
        df_total['　　感染者　　'] = df_l.iloc[:,-2]
    else:
        df_total['　　感染者　　'] = df_l.iloc[:,-1]

    # ### 都道府県別死亡者数（移動平均）
    data_ds = []
    for row in data_d:
        data_ds.append(row[-DAYS:])

    df_p = pd.DataFrame(data_ds,columns=df_h)
    df_s = []
    for row in data_d:
        df_s.append(sum(row))

    df_p.insert(0,'都道府県',pd.DataFrame(data_n))
    df_p.insert(1,'合計',pd.DataFrame(df_s))

    df_total['　　死亡者計　'] =  pd.DataFrame(df_s)
    if df_p.iloc[:,-1].sum() == 0:
        df_total['　　死亡者　　'] = df_p.iloc[:,-2]
    else:
        df_total['　　死亡者　　'] = df_p.iloc[:,-1]

    ## 死亡者合計
    df_ps = df_p.drop(['都道府県',"合計"],axis=1)
    df_ps = df_ps.T
    df_ps['死亡者'] = df_ps.sum(axis=1)
    # if df_ps['死亡者'].iat[-1] == 0:
    #     df_ps = df_ps.drop(df_ps.index[[len(df_ps)-1]])
    # else:
    #     df_ps = df_ps.drop(df_ps.index[[0]])

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

    df_t = df['testedCumulative'].diff()

    df_ta = list(df_t.rolling(7).mean())
    df_a['検査数'] = df_t
    df_a['検査数移動平均'] = df_ta

    df_a = df_a.rename(
        columns={'date':'日付','confirmed':"感染者数",'confirmedAvg7d':'感染者数移動平均',"criticalCumulative":'重症者数'}
        )

    df_bd = df_a['日付'].copy()
    df_d = pd.to_datetime(df_a['日付']).copy()
    df_a = df_a.drop('日付',axis=1)
    df_a = df_a.fillna(0).astype(int)
    df_show = df_a.tail(DAYS).copy()
    df_show['日付'] = df_bd.tail(DAYS)
    df_show['死亡者数'] = df_ps['死亡者'].values
    df_a['日付'] = df_d

    fig, ax1 = plt.subplots(figsize=(12,8))
    ax2 = ax1.twinx()
    ax1.bar(df_a['日付'].tail(DAYS),df_a['感染者数'].tail(DAYS),label='日次感染者数',color='lightgray')
    ax1.plot(df_a['日付'].tail(DAYS),df_a['感染者数移動平均'].tail(DAYS),label='感染者数移動平均',color='red',linewidth=2)
    ax2.plot(df_a['日付'].tail(DAYS),df_a['検査数移動平均'].tail(DAYS),label='検査数移動平均',color='green',linewidth=2)

    line_set(df_a,DAYS)

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

    # df_d = pd.to_datetime(df_a['日付'])
    # df_a = df_a.drop('日付',axis=1)
    # df_a = df_a.fillna(0).astype(int)
    # df_a['日付'] = df_d

    fig3, ax1 = plt.subplots(figsize=(12,8))

    # ax1.plot(df_a['日付'].tail(DAYS),df_a['重症者数'].tail(DAYS),label='重症者数',color='green')

    # line_set(df_a,DAYS)

    # title = "国内重傷者数 {}".format(update)
    # ax1.set_title(title)

    # ax1.set_xlabel('日付')
    # ax1.set_ylabel("重傷者（人）")

    # ax1.legend()
    # plt.grid(True)

    df_ps['重症者']= (df_a['重症者数'].tail(DAYS)).values

    df_ps['日付'] = df_a['日付'].tail(DAYS)

    # figp = make_subplots(
    #     rows=1, cols=2,
    #     subplot_titles=("重症者", "死亡者")
    #     )

    # figp.add_trace(
    #     go.Scatter(x=df_a['日付'].tail(DAYS),y=df_ps['重症者'],name='重症者'),
    #     row=1, col=1
    # )

    # figp.add_trace(
    #     go.Scatter(x=df_a['日付'].tail(DAYS),y=df_ps['死亡者'].rolling(7).mean(),name='死亡者（移動平均）'),
    #     row=1, col=2
    # )

## 東京都

    summary_json_t = tokyo_data()
 
    df_d = pd.DataFrame([row['diagnosed_date']] for row in summary_json_t['data'])
    df_r = pd.DataFrame([row['weekly_gain_ratio'],row['count']] for row in summary_json_t['data'])

    df_d = pd.to_datetime(df_d[0])
    df_r = df_r.fillna(0).astype(float)

    df_r['日付'] = df_d

    df = df_r.rename(columns={0:'感染率',1:'感染者数'}).copy()

    df = df.tail(DAYS)

    figt = plt.figure(figsize=(12,6))
    ax = figt.add_subplot(1,1,1)
    # ax1 = fig.add_subplot(2,2,2)
    ax1 = ax.twinx()
    ax.bar(df['日付'],df['感染者数'],color='lightgray')
    ax1.plot(df['日付'],df['感染率'])
    ax1.hlines(y=1,xmin=min(df['日付']),xmax=max(df['日付']),color='red')

    line_set(df,DAYS)

    plt.grid(True)
    title = "東京都感染者比率"
    ax.set_title(title)

    ax.set_xlabel('日付')
    ax1.set_ylabel("感染者比率")
    ax.set＿ylabel('感染者（人）')
    
    return fig,fig3,figt,df_show,update,df_l,df_d,df_p,df_ps,df,df_total,df_a

def main():
    DAYS = 300 #グラフ化する日数指定
    summary_json = data_load()
    fig,fig3,figt,df_show,update,df_l,df_d,df_p,df_ps,df,df_total,df_a = data_set(summary_json)

    st.sidebar.title('COVID-19 全国感染者情報')
    st.sidebar.subheader(update)

    option = st.sidebar.selectbox(
        '選択してください',
        ('全国感染者情報', '都道府県感染者情報', '東京都感染率')
        )
    st.sidebar.write(' ')
    st.sidebar.write('このサイトでは「日本国内の新型コロナウイルス (COVID-19) 感染状況追跡」(https://covid19japan.com)で作成されたデータを利用してます')
    st.sidebar.write(' ')
    st.sidebar.write('当日データは順次更新されますので、確定値はない場合があります')
    st.sidebar.write('公式発表数値と異なる場合があります')
    st.sidebar.write(' ')
    st.sidebar.write('streamlitで作成中')
    
    if option == '全国感染者情報':
        """
        ## 全国感染者情報
        ### 国内感染者数（移動平均）
        """
        st.pyplot(fig)
        # """
        # ### 国内重症者数
        # """
        # st.pyplot(fig3)
        """
        ### 国内重症者数・死亡者
        """
        radio = st.radio('対象データ',(('移動平均'
                                ,'実数'
                                )))
                                
        figp = make_subplots(
            rows=1, cols=2,
            subplot_titles=("重症者", "死亡者")
            )

        figp.add_trace(
            go.Scatter(x=df_a['日付'].tail(DAYS),y=df_ps['重症者'],name='重症者'),
            row=1, col=1
        )
        if radio == '移動平均':
            df_pss = df_ps['死亡者'].rolling(7).mean()
        else:
            df_pss = df_ps['死亡者']

        figp.add_trace(
            go.Scatter(x=df_a['日付'].tail(DAYS),y=df_pss,name='死亡者'),
            row=1, col=2
        )
        
        st.plotly_chart(figp)
        # """
        # ### 国内重症者数
        # """
        # st.line_chart(df_ps['重症者'])

        # """
        # ### 国内死亡者数（移動平均）
        # """
        # st.line_chart(df_ps['死亡者'].rolling(7).mean())

        """
        ### COVID-19感染者関連データ
        """
        st.dataframe(df_show[['日付','感染者数','検査数','重症者数','感染者数移動平均','検査数移動平均']].style.highlight_max(axis=0),height=400)
        st.write(
            'data: https://raw.githubusercontent.com/reustle/covid19japan-data/master/docs/summary/latest.json'
            )
        
    elif option == '都道府県感染者情報':
        """
        ## 都道府県感染者情報
        """
        dateList = [row['date'] for row in summary_json['daily']]

        df_date = pd.to_datetime(dateList)
        dateList_date = [datetime(row.year,row.month,row.day) for row in df_date[-DAYS:]]

        dateFrom = dateList_date[0]
        dateTo = dateList_date[-1]

        values = st.slider(
            '表示期間を指定してください',
                dateFrom, dateTo, (dateFrom, dateTo)
                )
        
        dateF = values[0]
        dateT = values[1]
        
        st.write('表示期間 ',str(dateF.year)+'/'+str(dateF.month)+'/'+str(dateF.day),
        '<------>',str(dateT.year)+'/'+str(dateT.month)+'/'+str(dateT.day))

        radio = st.radio('対象データ',(('移動平均'
                                        ,'実数'
                                        ,'実数(積み上げ棒グラフ）'
                                        )))
        
        erea_list = list(df_l['都道府県'].unique())
        selected_erea = st.multiselect('都道府県を選択してください', erea_list, default=erea_list[:5])
        df = df_l[(df_l['都道府県'].isin(selected_erea))]
        if len(df) > 0:
            df_lt = df.T
            df_lta = df_lt.drop(['都道府県','合計'],axis=0)
            df_lta['date'] = dateList_date
            df_lta = df_lta[(df_lta['date'] >= dateF) & (df_lta['date'] <= dateT)]

            data_index = df_lta['date']
            df_lta = df_lta.drop('date',axis=1)
            if radio == '移動平均':
                df_lta = df_lta.rolling(7).mean()
            dfl = df_lta.values.tolist()
            selected_erea = sorted(selected_erea)
            df_xx = pd.DataFrame(dfl,columns=selected_erea)
            df_xx = df_xx.set_index(data_index)

            df_xx1 = df_xx

            df = df_p[(df_p['都道府県'].isin(selected_erea))]

            df_lt = df.T
            df_lta = df_lt.drop(['都道府県','合計'],axis=0)
            df_lta['date'] = dateList_date
            df_lta = df_lta[(df_lta['date'] >= dateF) & (df_lta['date'] <= dateT)]

            data_index = df_lta['date']
            df_lta = df_lta.drop('date',axis=1)
            if radio == '移動平均':
                df_lta = df_lta.rolling(7).mean()
            dfl = df_lta.values.tolist()
            selected_erea = sorted(selected_erea)
            df_xx = pd.DataFrame(dfl,columns=selected_erea)
            df_xx = df_xx.set_index(data_index)

            df_xx2 = df_xx

            """
            ### 都道府県別感染者数
            """
            if radio == '移動平均':
                st.line_chart(df_xx1,use_container_width=True)
            elif radio == '実数':
                st.line_chart(df_xx1,use_container_width=True)
            else:
                st.bar_chart(df_xx1,use_container_width=True)
            """
            ### 都道府県別死亡者数
            """
            if radio == '移動平均':
                st.line_chart(df_xx2,use_container_width=True)
            elif radio == '実数':
                st.line_chart(df_xx2,use_container_width=True)
            else:
                st.bar_chart(df_xx2,use_container_width=True)
        else:
            """
            ## グラフ表示対象の都道府県が指定されていません
            """

        """
        ### 都道府県別感染者・死亡者関連データ
        """
        st.dataframe(df_total.style.highlight_max(axis=0))
    elif option == '東京都感染率':
        """
        ## 東京都感染率
        ### 東京都感染者比率
        """
        st.pyplot(figt)

        st.write(
            'data: https://raw.githubusercontent.com/tokyo-metropolitan-gov/covid19/development/data/daily_positive_detail.json'
            )


if __name__ == "__main__":
    main()
