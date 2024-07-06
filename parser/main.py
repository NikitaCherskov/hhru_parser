import requests
from bs4 import BeautifulSoup
import fake_useragent
import time
import mysql.connector

import asyncio
import uvicorn
from pydantic import BaseModel
from pydantic import Field
from typing import Optional
from typing import List
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
#import json



ua = fake_useragent.UserAgent()
ua_rand = ua.random
app = FastAPI(title="test_app")
templates = Jinja2Templates(directory="templates")



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



def get_blocks(text, amount):
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
    i = 0
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
                if i >= amount:
                    return
                yield resume
                i += 1
            print(page)
        except Exception as e:
            print(f"{e}")
        time.sleep(1)



def execute_in(sql_text, sql_values):
    try:
        connection = mysql.connector.connect(
        user='root', password='root', host='database', port="3306", database='db')
        #user='root', password='root', host='127.0.0.1', port="3306", database='db')
        print("DB connected")
        cursor = connection.cursor()
        cursor.execute(sql_text, sql_values)
        connection.commit()
    except Exception as e:
        print(f"{e}")

def execute_drop():
    try:
        connection = mysql.connector.connect(
        user='root', password='root', host='database', port="3306", database='db')
        #user='root', password='root', host='127.0.0.1', port="3306", database='db')
        print("DB connected")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM vacancies")
        connection.commit()
    except Exception as e:
        print(f"{e}")

def execute_out(filter):
    try:
        connection = mysql.connector.connect(
        user='root', password='root', host='database', port="3306", database='db')
        #user='root', password='root', host='127.0.0.1', port="3306", database='db')
        print("DB connected")
        cursor = connection.cursor()

        if filter == "":
            cursor.execute("Select * FROM vacancies")
            vacancies = cursor.fetchall()
            return vacancies
        else:
            query = "Select * FROM vacancies WHERE VacancyTitle = %s OR Experience = %s OR JobCreator = %s OR Adress = %s"
            cursor.execute(query, (filter, filter, filter, filter))
            vacancies = cursor.fetchall()
            return vacancies
    except Exception as e:
        print(f"{e}")
        return ""



def fill(amount : int, parser_request : str):
    #program start
    sql_text = ""
    i = 0
    for a in get_blocks(parser_request, amount):
        #print(a["name"], flush=True)
        name = a["name"]
        experience = a["experience"]
        job_creator = a["job_creator"]
        adress = a["adress"]
        sql_text = "INSERT INTO vacancies(VacancyTitle, Experience, JobCreator, Adress) VALUES(%s, %s, %s, %s)"
        sql_values = (name, experience, job_creator, adress)
        execute_in(sql_text, sql_values)
        i += 1




@app.get("/{amount}/{parser_request}")
def main_page(amount : int,
              parser_request : str,
              filter : str = ""):
    execute_drop()
    fill(amount, parser_request)
    return execute_out(filter)



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    #uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)