#!/usr/bin/env python
# coding: utf-8

# In[317]:


# 作成日：2019/03/26
# 作成者：japan-Derby-Dev Project Member
# 利用範囲：
# - 作成者が直接参画するプロジェクトの範囲に限る。
# - 他のプロジェクトへの利用禁止

import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
from urllib.parse import urljoin
import os.path
import time
import re
import datetime
import re

# テーブル情報からDataFrame生成する関数


def getRaceResult(URL):
    # 定数定義
    CLS_NAME = "race_table_01 nk_tb_common"

    html = requests.get(URL)
    soup = BeautifulSoup(html.content, 'html.parser')

    # テーブルを指定->レコード取得
    table = soup.findAll("table", {"class": CLS_NAME})[0]
    rows = table.findAll("tr")

    # カラム名取得
    c_names = []
    for row in rows:
        for cell in row.findAll('th'):
            c_names.append(cell.get_text())
    c_names.append('hourse_id')

    # インデックス取得(th分の1レコードを差し引く)
    idx = len(rows) - 1

    # DataFrame定義
    df = pd.DataFrame(columns=c_names, index=range(idx))

    # データをDataFrameに格納&逐次加工-----------------------------
    i = 0
    for row in rows:
        data = []
        for cell in row.findAll('td'):
            data.append(cell.get_text())
        if len(data) != 0:
            # 馬のページリンクをIDとして付与
            link = row.findAll('a')[0].get('href')
            link_split = link.split('/')
            data.append(link_split[-2])
            df.loc[i] = data
            i = i + 1
    # 発走取りやめになった馬を削除
    df = df[df['着順'] != '取']
    df = df[df['着順'] != '中']
    # ---------------------------------------------------------

    # データ加工１：馬体重/増減を分ける---------------------------
    for idx, data in enumerate(df['馬体重']):
        data_list = data.split('(')
        data_list[1] = data_list[1][:-1]
        df.at[idx, '馬体重'] = data_list[0]
        df.at[idx, '体重増減'] = data_list[1]
    # ---------------------------------------------------------

    # データ加工２：年齢/性別を分ける---------------------------
    for idx, data in enumerate(df['性齢']):
        df.at[idx, '性齢'] = data[0]
        df.at[idx, '年齢'] = data[1]
    # ---------------------------------------------------------

    # 使えない列を削除
    del_col = ['調教ﾀｲﾑ', '厩舎ｺﾒﾝﾄ', '備考', 'ﾀｲﾑ指数']
    df = df.drop(del_col, axis=1)

    return df


# ヘッダー情報からDataFrame生成する関数
def getRaceHeader(URL):
    # 定数定義
    CLS_NAME = "data_intro"

    html = requests.get(URL)
    soup = BeautifulSoup(html.content, 'html.parser')

    # カラムの定義（後処理で変更される）
    c_names = ['race_num', 'race_kind', 'race_type', 'race_info']
    df = pd.DataFrame(columns=c_names, )

    # レースヘッダーとなる情報を指定
    div = soup.findAll("div", {"class": CLS_NAME})[0]
    data_sets = div.findAll(['dt', 'h1', 'p'])

    row = []
    for i, data in enumerate(data_sets):
        row_data = data.get_text()
        row_data = row_data.replace(u'\n', u'')
        row_data = row_data.replace(u'\xa0\xa0', u' ')
        row_data = row_data.replace(u'\xa0/\xa0', u'/')
        row.append(row_data)

    df.loc[0] = row

    #データ加工処理１:race_typeを分割して付加-1 ---------------#
    ts = df.at[0, 'race_type'].split('/')
    df['race_type'] = ts[0]
    df['weather'] = ts[1][-1]
    df['ground_condition'] = ts[2][-1]
    df['dep_time'] = ts[3][4:]
    #-----------------------------------------------------#

    #データ加工処理１:race_typeを分割して付加-2 ---------------#
    # 分割後のカラム：
    #   1．race_distance(距離)
    #   2．ground_type(芝 / ダート種別)
    #   3．direction(回り方向 右か左か)
    #   4．inner_outside(内回り化外回りか)

    t = df.at[0, 'race_type']
    t = t.replace('m', '')
    pat = '\d+'

    t_distance = re.findall(pat, t)
    t_split_1 = re.split(pat, t)

    df['race_distance'] = t_distance[0]

    # ' 外'が含まれる場合（半角スペースでsplit）
    if re.search(' 外', t_split_1[0]) != None:
        t_split_2 = t_split_1[0].split(' ')
        df['ground_type'] = t_split_2[0][0]
        df['direction'] = t_split_2[0][1]
        df['inner_outside'] = t_split_2[1]

    # ' ダート'が含まれる場合
    elif re.search(' ダート', t_split_1[0]) != None:
        df['ground_type'] = t_split_1[0]
        df['direction'] = '-'
        df['inner_outside'] = '内'

    else:
        df['ground_type'] = t_split_1[0][0]
        df['direction'] = t_split_1[0][1]
        df['inner_outside'] = '内'

    # もともとのカラムを削除
    df = df.drop('race_type', axis=1)
    #-----------------------------------------------------#

    #データ加工処理２:race_infoを分割して付加 ---------------#
    ts = df.at[0, 'race_info'].split(' ')

    ts[0] = ts[0].replace('年', '-')
    ts[0] = ts[0].replace('月', '-')
    ts[0] = ts[0].replace('日', ' 00:00:00')
    df.at[0, 'date'] = str(
        datetime.datetime.strptime(ts[0], '%Y-%m-%d %H:%M:%S'))

    '''
    for idx, data in enumerate(ts):
        if len(ts[idx]) != 0:
            if idx==0:
                ts[idx] = ts[idx].replace('年','/')
                ts[idx] = ts[idx].replace('月','/')
                ts[idx] = ts[idx].replace('日','')
                df.at[0, 'date'] = datetime.datetime.strptime(ts[idx], '%Y/%m/%d')
            else :
                df['race_info_'+str(idx)] = ts[idx]           
    '''

    # もともとのカラム削除
    df = df.drop('race_info', axis=1)
    #-----------------------------------------------------#
    return df

# ヘッダーDataFrameとレース結果DataFrameを横結合


def combineDataFrame(r_df, h_df, fid=1):
    for idx in range((len(r_df))):
        h_df.loc[idx] = h_df.iloc[0]
    df = pd.concat([r_df, h_df], axis=1)

    # csv出力
    #file_name = "raceTable_" + str(fid) + ".csv"
    # df.to_csv(file_name)

    return df

# 開催レース一覧ページ（日別）からレースページのリンク配列を生成


def getLinks(URL):
    # 定数定義
    CLS_NAME = "race_top_data_info fc"

    html = requests.get(URL)
    soup = BeautifulSoup(html.content, 'html.parser')

    links = []
    # テーブルを指定->レコード取得
    races = soup.find_all("dl", {"class": CLS_NAME})

    for race in races:
        race_link = race.find('a').get('href')
        links.append(urljoin(URL, race_link))

    return links

# カレンダーからレースページURLを取得


def createRaceLinkFromCalender(URL):
    CLS_NAME = "race_calendar"

    html = requests.get(URL)
    soup = BeautifulSoup(html.content, 'html.parser')

    # テーブルを指定->レコード取得
    calendar = soup.findAll("div", {"class": CLS_NAME})[0]
    tds = calendar.find_all("td")
    links = []
    base = 'https://db.netkeiba.com/'
    for td in tds:
        race_link = td.find('a')
        if race_link is not None:
            race_link_url = race_link.get('href')
            links.append(urljoin(base, race_link_url))

    return links

# カレンダーから次の月のカレンダーページを取得


def createNextMonthLink(URL):
    CLS_NAME_1 = "race_calendar"
    CLS_NAME_2 = "next"

    html = requests.get(URL)
    soup = BeautifulSoup(html.content, 'html.parser')

    # テーブルを指定->レコード取得
    calendar = soup.findAll("div", {"class": CLS_NAME_1})[0]
    li = calendar.findAll('li', {'class': CLS_NAME_2})[0]
    next_month_link = li.find_all('a')[-1].get('href')

    next_month_url = urljoin(base, next_month_link)

    return next_month_url


# main処理---------------------------------------------------------------------
# **********************************************************
# ページリンクを辿って直近のレースまで再帰的にデータを取得
# 翌月のレースへ向かって処理を行う。
# そのため、スタートしたいU過去日のURLを初期引数に与えること。
# **********************************************************
# 初期URL
n_mon = 'https://db.netkeiba.com/?pid=race_kaisai&syusai=10&date=20190105'

merge_df = pd.DataFrame()
while True:
    r_links = createRaceLinkFromCalender(n_mon)
    time.sleep(1)

    for r_link in r_links:
        races = getLinks(r_link)
        time.sleep(1)

        # 取得したリンク配列を使ってcsvを連続生成
        for idx, url in enumerate(races):
            #print("URL: ",str(url))
            r_df = getRaceResult(url)
            h_df = getRaceHeader(url)
            df = combineDataFrame(r_df, h_df, idx)
            merge_df = pd.concat([merge_df, df])
            time.sleep(1)

    time.sleep(1)
    try:
        n_mon = createNextMonthLink(r_links[0])
        time.sleep(1)
    except:
        print("次月のカレンダーが・・・ない！？（処理を終了）")
        merge_df = merge_df.reset_index()
        merge_df.to_csv("race_merge.csv")
        break
# ------------------------------------------------------------------------------
