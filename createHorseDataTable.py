import requests
from bs4 import BeautifulSoup
import pandas as pd
from itertools import product
from urllib.parse import urljoin
import time

baseUrl = 'https://db.netkeiba.com/'


def getHorseHeader(soup):
    horseInfoTblCLSName = 'db_prof_table'
    raceResultTblCLSName = 'db_h_race_results nk_tb_common'

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


def getHorseData(soup, horseid):
    horseInfoTblCLSName = 'db_prof_table'
    bloodTblCLSName = 'blood_table'
    raceResultTblCLSName = 'db_h_race_results nk_tb_common'

    ### 基本情報取得 ###
    horseinfodata_list = []

    horseinfodata_list.append(horseid)

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
        raceData.append(horseid)

        index = 1
        for cell in row.findAll('td'):
            if index != 5:
                raceData.append(cell.get_text())
            else:
                raceData.append(cell.find('a').get('href'))
            index += 1
        horseraceresultdata_list.append(raceData)

    return horseinfodata_list, horseraceresultdata_list


def formatHorseInfo(horseinfo_df):
    # 基本情報データフレーム加工
    horseinfo_df["horse_name"] = horseinfo_df["horse_name"].str.strip()
    horseinfo_df["horse_age"] = horseinfo_df["horse_age"].str.strip()
    horseinfo_df["horse_father"] = horseinfo_df["horse_father"].str.strip()
    horseinfo_df["horse_paternalgrandfather"] = horseinfo_df["horse_paternalgrandfather"].str.strip()
    horseinfo_df["horse_paternalgrandmother"] = horseinfo_df["horse_paternalgrandmother"].str.strip()
    horseinfo_df["horse_mother"] = horseinfo_df["horse_mother"].str.strip()
    horseinfo_df["horse_maternalgrandfather"] = horseinfo_df["horse_maternalgrandfather"].str.strip()
    horseinfo_df["horse_maternalgrandmother"] = horseinfo_df["horse_maternalgrandmother"].str.strip()

    return horseinfo_df


def formatHorseRaceResult(horseraceresult_df):
    # レース結果情報データフレーム加工
    horseraceresult_df["レース名"] = horseraceresult_df["レース名"].str.split(
        "/", expand=True)[2]
    horseraceresult_df["コースタイプ"] = horseraceresult_df["距離"].str.get(0)
    horseraceresult_df["距離"] = horseraceresult_df["距離"].str.strip("芝|ダ|障")
    #horseraceresult_df["通過平均"] = horseraceresult_df["通過"].str.split("-", expand=True).astype(float).mean(axis=1, skipna=True)
    horseraceresult_df["ペース前半"] = horseraceresult_df["ペース"].str.split(
        "-", expand=True)[0]
    horseraceresult_df["ペース後半"] = horseraceresult_df["ペース"].str.split(
        "-", expand=True)[1]
    horseraceresult_df["馬体重増減"] = horseraceresult_df["馬体重"].str.split(
        "(", expand=True)[1]
    horseraceresult_df["馬体重増減"] = horseraceresult_df["馬体重増減"].str.strip(")")
    horseraceresult_df["馬体重"] = horseraceresult_df["馬体重"].str.split(
        "(", expand=True)[0]

    return horseraceresult_df


def getHourseLinksFromRacePage(URL):
    CLS_NAME = "race_table_01 nk_tb_common"

    html = requests.get(URL)
    soup = BeautifulSoup(html.content, 'html.parser')

    RaceResultTbl = soup.findAll(
        'table', {'class': CLS_NAME})[0]
    rows = RaceResultTbl.findAll('tr')

    links = []
    for row in rows:
        index = 1
        for cell in row.findAll('td'):
            if index == 4:
                links.append(cell.find('a').get('href'))
            index += 1

    return links


def getRaceLinksFromEventDatePage(URL):
    # 開催レース一覧ページ（日別）からレースページのリンク配列を生成
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


def getEventDateLinksFromCalender(URL):
    # カレンダーからレースページURLを取得
    CLS_NAME = "race_calendar"

    html = requests.get(URL)
    soup = BeautifulSoup(html.content, 'html.parser')

    # テーブルを指定->レコード取得
    calendar = soup.findAll("div", {"class": CLS_NAME})[0]
    tds = calendar.find_all("td")
    links = []
    for td in tds:
        race_link = td.find('a')
        if race_link is not None:
            race_link_url = race_link.get('href')
            links.append(urljoin(baseUrl, race_link_url))
    return links


def createNextMonthLink(URL):
    # カレンダーから次の月のカレンダーページを取得
    CLS_NAME_1 = "race_calendar"
    CLS_NAME_2 = "next"

    html = requests.get(URL)
    soup = BeautifulSoup(html.content, 'html.parser')

    # テーブルを指定->レコード取得
    calendar = soup.findAll("div", {"class": CLS_NAME_1})[0]
    li = calendar.findAll('li', {'class': CLS_NAME_2})[0]
    next_month_link = li.find_all('a')[-1].get('href')

    next_month_url = urljoin(baseUrl, next_month_link)

    return next_month_url


###########################################################
# main
###########################################################
# 初期設定
n_mon = 'https://db.netkeiba.com/?pid=race_kaisai&syusai=10&date=20190302'

merge_info_df = pd.DataFrame()
merge_raceresult_df = pd.DataFrame()
total = 1

while True:
    ed_links = getEventDateLinksFromCalender(n_mon)
    time.sleep(1)

    for ed_link in ed_links:
        r_links = getRaceLinksFromEventDatePage(ed_link)
        time.sleep(1)

        for r_link in r_links:
            h_links = getHourseLinksFromRacePage(r_link)
            time.sleep(1)

            for h_link in h_links:
                horseurl = urljoin(baseUrl, h_link)
                horseid = horseurl.replace(
                    'https://db.netkeiba.com/horse/', '').replace('/', '')

                # 馬ページ取得
                html = requests.get(horseurl)
                soup = BeautifulSoup(html.content, 'lxml')

                print(str(total) + "番目:" + horseurl)
                horseinfo_header, horseraceresult_header = getHorseHeader(soup)
                horseinfo_data, horseraceresult_data = getHorseData(
                    soup, horseid)

                # データフレーム取得
                horseinfo_df = pd.DataFrame(
                    [horseinfo_data], columns=horseinfo_header)
                horseraceresult_df = pd.DataFrame(
                    horseraceresult_data, columns=horseraceresult_header)

                # データフレーム結合
                merge_info_df = pd.concat(
                    [merge_info_df, horseinfo_df], sort=True)
                merge_raceresult_df = pd.concat(
                    [merge_raceresult_df, horseraceresult_df.drop(0)], sort=True)

                total += 1
                time.sleep(0.5)

    try:
        n_mon = createNextMonthLink(r_links[0])
        time.sleep(1)
    except:
        print("次月のカレンダーが・・・ない！？（処理を終了）")
        break


# データフレーム加工
formatHorseInfo(merge_info_df)
formatHorseRaceResult(merge_raceresult_df)

# データフレームCSV出力
merge_info_df.to_csv("horse.csv")
merge_raceresult_df.to_csv("horseraceresult.csv")
