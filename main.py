import requests
from bs4 import BeautifulSoup

url = 'https://db.netkeiba.com/horse/2013105889/'

html = requests.get(url)
soup = BeautifulSoup(html.content, 'lxml')

# 馬ID
horseID = url.replace("https://db.netkeiba.com/horse/","").replace("/","")
print("馬ID：" + horseID)

# 馬名
horseName = soup.select_one("#db_main_box > div.db_head.fc > div.db_head_name.fc > div.horse_title > h1").string
print("馬名：" + horseName)

# 年齢
horseAge = soup.select_one("#db_main_box > div.db_head.fc > div.db_head_name.fc > div.horse_title > p.txt_01").string
print("年齢：" + horseAge)


#################
#ここから先未クリア
#################
# 調教師
horseTrainer = soup.select_one("#db_main_box > div.db_main_deta > div > div.db_prof_area_02 > table > tbody > tr:nth-of-type(2) > td > a")
print("調教師：" + horseTrainer)

# 馬主
horseOwner = soup.select_one("#db_main_box > div.db_main_deta > div > div.db_prof_area_02 > table > tbody > tr:nth-of-type(3) > td > a").string
print("馬主：" + horseOwner)

# 獲得総賞金
horseTotalPrizeMoney = soup.select_one("#db_main_box > div.db_main_deta > div > div.db_prof_area_02 > table > tbody > tr:nth-of-type(7) > td")
print("獲得総賞金：" + horseTotalPrizeMoney)

# 父馬
horseFather = soup.select_one("#db_main_box > div.db_main_deta > div > div.db_prof_area_02 > div > dl > dd > table > tbody > tr:nth-of-type(1) > td:nth-of-type(1) > a").string
print("父馬：" + horseFather)

# 母馬
horseMother = soup.select_one("#db_main_box > div.db_main_deta > div > div.db_prof_area_02 > div > dl > dd > table > tbody > tr:nth-of-type(3) > td.b_fml > a").string
print("母馬：" + horseMother)