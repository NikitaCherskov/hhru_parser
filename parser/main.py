import requests
from bs4 import BeautifulSoup
import fake_useragent
import time
import mysql.connector
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
    try:
        experience = soup.find("span", attrs = {"data-qa":"vacancy-experience"}).text
    except:
        experience = ""
    try:
        employment_mode = soup.find("p", attrs = {"class":"vacancy-description-list-item","data-qa":"vacancy-view-employment-mode"}).text
    except:
        employment_mode = ""
    resume = {
        "name":name,
        "experience":experience,
        "employment_mode":employment_mode
    }
    return resume



def get_blocks(text):
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
            for cards in soup2.find_all("div", attrs={"class":"vacancy-card--z_UXteNo7bRGzxWVcL7y font-inter"}):
                try:
                    name = cards.find("span", attrs={"data-qa":"serp-item__title"}).text
                except:
                    name = ""
                try:
                    experience = cards.find("span", attrs={"data-qa":"vacancy-serp__vacancy-work-experience"}).text
                except:
                    experience = ""
                try:
                    job_creator = cards.find("span", attrs={"class":"company-info-text--vgvZouLtf8jwBmaD1xgp"}).text
                except:
                    job_creator = ""
                try:
                    adress = cards.find("span", attrs={"data-qa":"vacancy-serp__vacancy-address"}).text
                except:
                    adress = ""
                resume = {
                    "name":name,
                    "experience":experience,
                    "job_creator":job_creator,
                    "adress":adress
                }
                yield resume
            print(page)
        except Exception as e:
            print(f"{e}")
        time.sleep(1)



def execute(sql_text):
    try:
        connection = mysql.connector.connect(
        user='root', password='root', host='database', port="3306", database='db')
        print("DB connected")
        cursor = connection.cursor()
        cursor.execute(sql_text)
    except Exception as e:
        print(f"{e}")
    time.sleep(1)



if __name__ == "__main__":
    sql_text = ""
    i = 0
    for a in get_blocks("python"):
        #print(a["name"], flush=True)
        name = a["name"]
        experience = a["experience"]
        job_creator = a["job_creator"]
        adress = a["adress"]
        sql_text += f"INSERT INTO Vacancies(VacancyTitle, Experience, JobCreator, Adress) VALUES(\"{name}\",\"{experience}\",\"{job_creator}\",\"{adress}\");\n"
        if(i >= 10):
            execute(sql_text)
            sql_text = ""
            i = 0
        i += 1