import requests
from bs4 import BeautifulSoup
import fake_useragent
import time
#import json


    
ua = fake_useragent.UserAgent()
ua_rand = ua.random


def get_links(text):
    #заходит на hh
    data = requests.get(
        url = f"https://hh.ru/search/vacancy?text={text}&area=1&page=1",
        headers = {"user-agent":ua_rand}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")

    #ищет количество страниц
    try:
        page_count_txt = soup.find("div", attrs={"class":"pager"}).find_all("span", recursive=False)[-1].find("a", attrs={"class":"bloko-button"}).find("span").text
        page_count = int(page_count_txt)
    except:
        return

    #проходит по всем страницам
    for page in range(page_count):
        try:
            data2 = requests.get(
                url = f"https://hh.ru/search/vacancy?text={text}&area=1&page={page}",
                headers = {"user-agent":ua_rand}
            )
            if data2.status_code != 200:
                continue
            soup2 = BeautifulSoup(data2.content, "lxml")
            for a in soup2.find_all("a", attrs={"class":"bloko-link","target":"_blank","data-qa":""}):
                #yield f"{a.attrs['href'].split('?')[0]}"
                yield f"{a.attrs['href']}"
        except Exception as e:
            print(f"{e}")
        time.sleep(1)




def get_resume(link):
    time.sleep(1)
    try:
        data = requests.get(
            url = link,
            headers = {"user-agent":ua_rand}
        )
    except requests.exceptions.ConnectionError as e:
        print("Connection refused:" + str(e))
        return "None"
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        name = soup.find("h1", attrs = {"class":"bloko-header-section-1","data-qa":"vacancy-title"}).text
    except:
        name = ""
    resume = {
        "name":name
    }
    return resume



if __name__ == "__main__":
    for a in get_links("python"):
        print(get_resume(a), flush = True)
        #print(a)