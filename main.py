import requests
from bs4 import BeautifulSoup

url = 'https://db.netkeiba.com/horse/2013105880/'

html = requests.get(url)
soup = BeautifulSoup(html.content, 'lxml')

# 馬ID
horseID = url.replace("https://db.netkeiba.com/horse/","").replace("/","")
print("馬ID：" + horseID)

# 馬名
horseName = soup.select("#db_main_box > div.db_head.fc > div.db_head_name.fc > div.horse_title > h1")
print("馬名：" + horseName)

# 年齢
horseAge = soup.select("#db_main_box > div.db_head.fc > div.db_head_name.fc > div.horse_title > p.txt_01")
print("年齢：" + horseAge)

# 調教師
horseTrainer = soup.select("#db_main_box > div.db_main_deta > div > div.db_prof_area_02 > table > tbody > tr:nth-child(2) > td > a")
print("調教師：" + horseTrainer)

# 馬主
horseOwner = soup.select("#db_main_box > div.db_main_deta > div > div.db_prof_area_02 > table > tbody > tr:nth-child(3) > td > a")
print("馬主：" + horseOwner)

# 獲得総賞金
horseTotalPrizeMoney = soup.select("#db_main_box > div.db_main_deta > div > div.db_prof_area_02 > table > tbody > tr:nth-child(7) > td")
print("獲得総賞金：" + horseTotalPrizeMoney)

# 父馬
horseFather = soup.select("#db_main_box > div.db_main_deta > div > div.db_prof_area_02 > div > dl > dd > table > tbody > tr:nth-child(1) > td:nth-child(1) > a")
print("父馬：" + horseFather)

# 母馬
horseMother = soup.select("#db_main_box > div.db_main_deta > div > div.db_prof_area_02 > div > dl > dd > table > tbody > tr:nth-child(3) > td.b_fml > a")
print("母馬：" + horseMother)