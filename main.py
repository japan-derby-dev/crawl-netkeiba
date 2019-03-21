import requests
from bs4 import BeautifulSoup
import pandas as pd

# スクレイピングに利用するクラス名
horseInfoTblCLSName = 'db_prof_table no_OwnerUnit'
bloodTblCLSName = 'blood_table'
raceResultTblCLSName = 'db_h_race_results nk_tb_common'


def parseHorseInfoHeader(soup):
    c_name = []
    c_name.append('horse_id')
    c_name.append('horse_name')
    c_name.append('horse_age')

    # 基本情報
    horseInfoTbl = soup.findAll('table', {'class': horseInfoTblCLSName})[0]
    rows = horseInfoTbl.findAll('tr')
    for row in rows:
        for cell in row.findAll('th'):
            c_name.append(cell.get_text())

    c_name.append('horse_father')
    c_name.append('horse_paternalgrandfather')
    c_name.append('horse_paternalgrandmother')
    c_name.append('horse_mother')
    c_name.append('horse_maternalgrandfather')
    c_name.append('horse_maternalgrandmother')

    return c_name


def parseHorseInfoData(soup):

    data = []

    # 馬ID
    data.append(url.replace(
        'https://db.netkeiba.com/horse/', '').replace('/', ''))

    # 馬名
    data.append(soup.select_one(
        "#db_main_box > div.db_head.fc > div.db_head_name.fc > div.horse_title > h1").string)

    # 年齢
    data.append(soup.select_one(
        "#db_main_box > div.db_head.fc > div.db_head_name.fc > div.horse_title > p.txt_01").string)

    # 基本情報
    horseInfoTbl = soup.findAll('table', {'class': horseInfoTblCLSName})[0]
    rows = horseInfoTbl.findAll('tr')
    for row in rows:

        for cell in row.findAll('td'):
            data.append(cell.get_text())

    # 血統情報
    bloodTbl = soup.findAll('table', {'class': bloodTblCLSName})[0]
    rows = bloodTbl.findAll('tr')
    for row in rows:
        for cell in row.findAll('td'):
            data.append(cell.get_text())

    return data


def parseHorseRaceResultHeader(soup):
    c_name = []
    c_name.append('horse_id')

    horseInfoTbl = soup.findAll('table', {'class': raceResultTblCLSName})[0]
    rows = horseInfoTbl.findAll('tr')

    for row in rows:
        for cell in row.findAll('th'):
            c_name.append(cell.get_text())

    return c_name


def parseHorseRaceResultData(soup):
    horseInfoTbl = soup.findAll('table', {'class': raceResultTblCLSName})[0]
    rows = horseInfoTbl.findAll('tr')

    data = []
    for row in rows:
        raceData = []
        raceData.append(url.replace(
            'https://db.netkeiba.com/horse/', '').replace('/', ''))

        for cell in row.findAll('td'):
            raceData.append(cell.get_text())

        data.append(raceData)

    return data


######################################################################
# main
######################################################################
url = 'https://db.netkeiba.com/horse/2002100816/'
html = requests.get(url)
soup = BeautifulSoup(html.content, 'lxml')

# horse取得
horse_header = parseHorseInfoHeader(soup)
horse_data = []
horse_data.append(parseHorseInfoData(soup))
horse_data.append(parseHorseInfoData(soup))

horse_df = pd.DataFrame(horse_data, columns=horse_header)
horse_df.to_csv("horse.csv")

# horse_race_result取得
horse_race_result_header = parseHorseRaceResultHeader(soup)
horse_race_result_data = parseHorseRaceResultData(soup)

horse_race_result_df = pd.DataFrame(
    horse_race_result_data, columns=horse_race_result_header)
horse_race_result_df.to_csv("horse_race_result.csv")
