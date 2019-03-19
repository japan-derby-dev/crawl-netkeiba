#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

#テーブル情報からDataFrame生成する関数
def getRaceResult(URL):
    #定数定義
    CLS_NAME = "race_table_01 nk_tb_common"
    
    html = requests.get(URL)
    soup = BeautifulSoup(html.content, 'html.parser')

    #テーブルを指定->レコード取得
    table = soup.findAll("table",{"class":CLS_NAME})[0]
    rows = table.findAll("tr")

    #カラム名取得
    c_names = []
    for row in rows:
        for cell in row.findAll('th'):
            c_names.append(cell.get_text())
    c_names.append('hourse_id')
    
    #インデックス取得(th分の1レコードを差し引く)
    idx = len(rows) - 1

    #DataFrame定義
    df = pd.DataFrame(columns=c_names, index=range(idx))

    #データをDataFrameに格納&逐次加工-----------------------------
    i = 0;
    for row in rows:
        data = []
        for cell in row.findAll('td'):
            data.append(cell.get_text())            
        if len(data) != 0:
            #馬のページリンクをIDとして付与
            link = row.findAll('a')[0].get('href')
            link_split = link.split('/')
            data.append(link_split[-2])            
            df.loc[i] = data
            i = i + 1
    #---------------------------------------------------------
    
    #データ加工１：馬体重と増減を分ける---------------------------
    for idx, data in enumerate(df['馬体重']):
        data_list = data.split('(')
        data_list[1] = data_list[1][:-1]
        df.at[idx, '馬体重'] = data_list[0]
        df.at[idx, '体重増減'] = data_list[1]
    #---------------------------------------------------------
    
    #データ加工２：年齢と性別を分ける---------------------------
    for idx, data in enumerate(df['性齢']):
        df.at[idx, '性齢'] = data[0]
        df.at[idx, '年齢'] = data[1]
    #---------------------------------------------------------
    
    return df


#ヘッダー情報からDataFrame生成する関数
def getRaceHeader(URL):
    #定数定義
    CLS_NAME = "data_intro"

    html = requests.get(URL)
    soup = BeautifulSoup(html.content, 'html.parser')

    #カラムの定義（後処理で変更される）
    c_names = ['race_num','race_kind','race_type','race_info','date','detail','sex','syokin']
    df = pd.DataFrame(columns=c_names)

    #レースヘッダーとなる情報を指定
    div = soup.findAll("div",{"class":CLS_NAME})[0]
    data_sets = div.findAll(['dt','h1','p'])
    row = []
    for i,data in enumerate(data_sets):      
        row_data = data.get_text()
        row.append(row_data)

    df.loc[0] = row
    
    #データ加工処理１:race_typeを分割して付加---------------#
    t = df.at[0,'race_type']
    t_1 = t[:1]
    t = t[1:]
    tmp_t = t.split('m')
    
    df['ground_type'] = t_1
    df['race_distance'] = tmp_t[0]
    df['direction'] = tmp_t[1]
    
    #もともとのカラムを削除
    df = df.drop('race_type', axis=1)
    #-----------------------------------------------------#
    
    #データ加工処理２:race_typeを分割して付加---------------#
    s = df.at[0, 'race_info']
    tmp_s = s.split("/")
    
    df['weather'] = tmp_s[0]
    df['ground_condition'] = tmp_s[1]    
    #発走タイムは捨てる。
    #もともとのカラムを削除
    df = df.drop('race_info', axis=1)
    #-----------------------------------------------------#

    #データ加工処理３:dateから日付だけ取得--------------#
    u = df.at[0, 'date']
    df['date'] = u.split("(")[0]    
    #-----------------------------------------------------#
    
    return df

#ヘッダーDataFrameとレース結果DataFrameを横結合
def conbinDataFrame(r_df, h_df):
    for idx in range((len(r_df))):
        h_df.loc[idx] = h_df.iloc[0]
    df = pd.concat([r_df, h_df], axis=1)
    
    #csv出力
    df.to_csv("merge_raceTable.csv")
    
    return df

#確認用
url = 'https://race.netkeiba.com/?pid=race&id=c201906020802&mode=result'
r_df = getRaceResult(url)
h_df = getRaceHeader(url)
df = conbinDataFrame(r_df, h_df)
df

