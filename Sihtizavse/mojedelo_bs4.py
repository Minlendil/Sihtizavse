from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import re
from pandas import DataFrame


def date_trans(text):
    if text == "Danes":
        return datetime.today().strftime("%d.%m.%Y")
    elif text == "Včeraj":
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        return yesterday.strftime("%d.%m.%Y")
    else:
        return text


def text_trans(opis):
    if len(opis) <= 250:
        return opis
    else:
        return opis[0:247] + "..."


# Tujina ima dejansko dic_key 53, vendar je tako bolj elegantno
list_of_regions = {2:"Pomurska", 4:"Podravska", 5:"Koroška", 6:"Savinjska", 1:"Zasavska", 9:"Posavska",
                3:"Jugovzhodna Slovenija", 12:"Osrednjeslovenska", 7:"Gorenjska", 8:"Primorsko-notranjska",
                10:"Goriška", 11:"Obalno-kraška", 13: "Tujina"}

base=("https://www.mojedelo.com/prosta-delovna-mesta/napredno-iskanje?q=&rids=")


def mojedelo():
    list_of_dics = []
    for regija_link in range(1, 14):
        if regija_link == 13:
            link_to_site = (base + str(53))
        else:
            link_to_site = (base + str(regija_link))
        name_of_region = list_of_regions[regija_link]
        # print(link_to_site)
        # print(name_of_region)
        r = requests.get(link_to_site)
        c = r.content
        soup = BeautifulSoup(c, "html.parser")
        all = soup.find("div", "PagedList-pager").find_all("li")
        if len(all) >= 14:
            number_of_pages = all[-1].text
        else:
            number_of_pages = all[-2].text
        for page_link in range(1,int(number_of_pages)+1):
            link_to_page = (link_to_site + "&p=" + str(page_link))
            r = requests.get(link_to_page)
            c = r.content
            soup = BeautifulSoup(c, "html.parser")
            jobs = soup.find_all(attrs={"class": re.compile('w-inline-block job-ad')})
            for job_data in jobs:
                try:
                    link_to_job = job_data.find(href=True)["href"].split("?", 1)[0]
                except TypeError:
                    link_to_job = job_data["href"].split("?", 1)[0]
                d = {}
                d["Title"] = job_data.find("h2","title").text
                box_item = job_data.find_all("div", "boxItemGroup")
                d["Application_date"] = "/"
                d["Place_of_work"] = box_item[2].text.replace("\n", "")
                d["Company"] = box_item[1].text.replace("\n", "")
                d["Url"] = "https://www.mojedelo.com" + link_to_job
                try:
                    d["Description"] = text_trans(job_data.find("p").text).replace("\n", "").replace(
                        "\r", "").replace("\t", "").replace("\xa0", "")
                except AttributeError:
                    r = requests.get("https://www.mojedelo.com" + link_to_job)
                    c = r.content
                    soup = BeautifulSoup(c, "html.parser")
                    try:
                        d["Description"] = text_trans(soup.find("p").text).replace("\n", "").replace(
                        "\r", "").replace("\t", "").replace("\xa0", "")
                    except AttributeError:
                        d["Description"] = "/"
                d["Date_of_announcement"] = date_trans(box_item[0].text.replace("\n", "").replace(" ", ""))
                d["Region"] = name_of_region
                d["Site"] = "mojedelo.com"
                #print(d)
                #print("------------------------------")
                list_of_dics.append(d)

    df = DataFrame(list_of_dics)
    df = df.drop_duplicates(subset=["Title","Company","Place_of_work"])
    df.to_csv("ScraperData/mojedelo.csv", index=False)
    print("Mojedelo končan!")
    print("število zadetkov: " + str(len(df)))
    print("--------------------------------------")


