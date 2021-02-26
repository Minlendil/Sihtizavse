from bs4 import BeautifulSoup
import requests
from pandas import DataFrame, read_csv
from datetime import date, timedelta, datetime


def form_text(opis):
    if len(opis) <= 250:
        return opis
    else:
        return opis[0:247] + "..."


list_of_regions = {28:"Pomurska", 27:"Podravska", 23:"Koroška", 29:"Savinjska", 31:"Zasavska", 30:"Posavska",
                22:"Jugovzhodna Slovenija", 26:"Osrednjeslovenska", 20:"Gorenjska", 24:"Primorsko-notranjska",
                21:"Goriška", 25:"Obalno-kraška", 32: "Tujina"}

base=("https://www.optius.com/iskalci/prosta-delovna-mesta/?Time=1&Keywords=&Regions[]=")


def optius():
    list_of_dics = []
    df_bf = read_csv("ScraperData/optius.csv")

    for index, row in df_bf.iterrows():
        if date.today() - timedelta(days=30) < (datetime.strptime(row["Date_of_announcement"], "%d.%m.%Y")).date():
            list_of_dics.append(row.to_dict())

    print("Start optius")
    for regija_link in range(20,33):
        link_to_site=(base+str(regija_link))
        name_of_region = list_of_regions[regija_link]
        #print(link_to_site)
        #print(name_of_region)
        r = requests.get(link_to_site)
        c = r.content
        soup = BeautifulSoup(c, "html.parser")
        all = soup.find("div", "pagination")
        # try da preveri če je samo ena stran z zadetki/delovnimi mesti ali jih je več. Če je samo ena gre na except.
        try:
            num_of_li = len(all.find_all("li")) - 1
            if num_of_li < 7:
                number_of_pages = num_of_li
            else:
                number_of_pages = int(all.find("li", "pn pn-7").text)

        except AttributeError:
            number_of_pages = 1
        #print(number_of_pages)

        for page_link in range(0, number_of_pages * 20, 20):
            link_to_page = (link_to_site + "&s=" + str(page_link))
            # print(link_to_page)
            r = requests.get(link_to_page)
            c = r.content
            soup = BeautifulSoup(c, "html.parser")
            all = soup.find("div", "job-results-list")
            jobs = all.find("ul").find_all("li", recursive=False)
            for job_data in jobs:
                link_to_job = job_data.find(href=True)
                #print(link_to_job["href"])
                d = {}
                r = requests.get("https://www.optius.com" + link_to_job["href"])
                c = r.content
                soup = BeautifulSoup(c, "html.parser")
                header_data = soup.find("div", "main-info-header")
                d["Title"] = header_data.find("h1").text
                d["Application_date"] = header_data.find_all("li")[1].text.replace("Prijave do:", "").replace(" ", "")
                d["Place_of_work"] = header_data.find_all("li")[2].text.replace("\n", "").replace("Kraj dela:", "")
                d["Company"] = header_data.find("h4").text
                d["Url"] = "https://www.optius.com" + link_to_job["href"]
                try:
                    d["Description"] = form_text(soup.find("div", "company-content").text)
                except AttributeError:
                    d["Description"] = "/"
                d["Date_of_announcement"] = header_data.find_all("li")[0].text.replace("Datum objave:", "").replace(" ", "")
                d["Region"] = name_of_region
                d["Site"] = "optius.com"
                #print(d)
                #print("-----------------------------")
                list_of_dics.append(d)

    df = DataFrame(list_of_dics)
    df = df.drop_duplicates(subset=["Title", "Company", "Place_of_work"])
    df.to_csv("ScraperData/optius.csv", index=False)
    print("Optius končan!")
    print("število zadetkov: " + str(len(df)))
    print("--------------------------------------")
