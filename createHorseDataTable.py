import requests
from bs4 import BeautifulSoup
import pandas as pd
from itertools import product
import time

# スクレイピングに利用するクラス名
horseInfoTblCLSName = 'db_prof_table no_OwnerUnit'
bloodTblCLSName = 'blood_table'
raceResultTblCLSName = 'db_h_race_results nk_tb_common'


def getHorseHeader(url):
    # 馬ページ取得
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'lxml')

    ### 基本情報のヘッダ取得 ###
    horseinfoheader_list = []
    horseinfoheader_list.append('horse_id')
    horseinfoheader_list.append('horse_name')
    horseinfoheader_list.append('horse_age')

    horseInfoTbl = soup.findAll('table', {'class': horseInfoTblCLSName})[0]
    rows = horseInfoTbl.findAll('tr')
    for row in rows:
        for cell in row.findAll('th'):
            horseinfoheader_list.append(cell.get_text())

    horseinfoheader_list.append('horse_father')
    horseinfoheader_list.append('horse_paternalgrandfather')
    horseinfoheader_list.append('horse_paternalgrandmother')
    horseinfoheader_list.append('horse_mother')
    horseinfoheader_list.append('horse_maternalgrandfather')
    horseinfoheader_list.append('horse_maternalgrandmother')

    ### レース結果のヘッダ取得 ###
    horseraceresultheader_list = []
    horseraceresultheader_list.append('horse_id')

    horseInfoTbl = soup.findAll('table', {'class': raceResultTblCLSName})[0]
    rows = horseInfoTbl.findAll('tr')

    for row in rows:
        for cell in row.findAll('th'):
            horseraceresultheader_list.append(cell.get_text())

    # 二つのヘッダ配列を返却
    return horseinfoheader_list, horseraceresultheader_list


def getHorseData(url):
    # 馬ページ取得
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'lxml')

    ### 基本情報取得 ###
    horseinfodata_list = []

    horseinfodata_list.append(url.replace(
        'https://db.netkeiba.com/horse/', '').replace('/', ''))

    # 馬名
    horseinfodata_list.append(soup.select_one(
        "#db_main_box > div.db_head.fc > div.db_head_name.fc > div.horse_title > h1").string)

    # 年齢
    horseinfodata_list.append(soup.select_one(
        "#db_main_box > div.db_head.fc > div.db_head_name.fc > div.horse_title > p.txt_01").string)

    # その他
    horseInfoTbl = soup.findAll('table', {'class': horseInfoTblCLSName})[0]
    rows = horseInfoTbl.findAll('tr')
    for row in rows:

        for cell in row.findAll('td'):
            horseinfodata_list.append(cell.get_text())

    # 血統情報
    bloodTbl = soup.findAll('table', {'class': bloodTblCLSName})[0]
    rows = bloodTbl.findAll('tr')
    for row in rows:
        for cell in row.findAll('td'):
            horseinfodata_list.append(cell.get_text())

    ### レース結果情報取得 ###
    horseRaceResultTbl = soup.findAll(
        'table', {'class': raceResultTblCLSName})[0]
    rows = horseRaceResultTbl.findAll('tr')

    horseraceresultdata_list = []
    for row in rows:
        raceData = []
        raceData.append(url.replace(
            'https://db.netkeiba.com/horse/', '').replace('/', ''))

        for cell in row.findAll('td'):
            raceData.append(cell.get_text())

        horseraceresultdata_list.append(raceData)

    return horseinfodata_list, horseraceresultdata_list


###########################################################
# main
###########################################################
url = 'https://db.netkeiba.com/horse/2016102227/'
horseinfo_header, horseraceresult_header = getHorseHeader(url)
horseinfo_data, horseraceresult_data = getHorseData(url)

# データフレーム作成
horseinfo_df = pd.DataFrame([horseinfo_data], columns=horseinfo_header)
horseraceresult_df = pd.DataFrame(
    horseraceresult_data, columns=horseraceresult_header)

# データフレームCSV出力
horseinfo_df.to_csv("horse.csv")
horseraceresult_df.to_csv("horseraceresult.csv")
