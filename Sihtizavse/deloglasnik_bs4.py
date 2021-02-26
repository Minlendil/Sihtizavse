from bs4 import BeautifulSoup
import requests
import re
from pandas import DataFrame

"""Verjetno se pojavljajo duplikati v končni tabeli. Število zapisov v Dataframu je večje od števila ponujenih delovnih 
mest na strani sami."""

def form_text(opis):

    opis = opis.replace("\n"," ").replace("\r","").replace("\t","").replace("Opis delovnega mesta","")
    if len(opis) <= 250:
        return opis
    else:
        return opis[0:247] + "..."


def form_date(opis):
    last_char_index = opis.rfind(".")
    return opis[:last_char_index]

list_of_regions = {2:"Pomurska", 3:"Podravska", 4:"Koroška", 5:"Savinjska", 6:"Zasavska", 7:"Posavska",
                8:"Jugovzhodna Slovenija", 9:"Osrednjeslovenska", 10:"Gorenjska", 11:"Primorsko-notranjska",
                12:"Goriška", 13:"Obalno-kraška", 14: "Tujina"}

base=("https://www.deloglasnik.si/Iskanje-zaposlitve/?searchWord=&keyword=&job_title=&job_title_id=&area=")


def deloglasnik():
    list_of_dics = []
    for regija_link in range(2,15):
        link_to_site=(base+str(regija_link))
        name_of_region = list_of_regions[regija_link]
        # print(link_to_site)
        r = requests.get(link_to_site)
        c = r.content
        soup = BeautifulSoup(c, "html.parser")
        try:
            all = soup.find("li",{"class":"last icon"})
            string = all.find(href=True)["href"]
            if string[-2].isdigit():
                number_of_pages=int(string[-2:])
            else:
                number_of_pages=int(string[-1])
            # print(number_of_pages)
        except:
            number_of_pages=1
        for page_link in range(1,number_of_pages+1):
            link_to_page=(link_to_site+"&page="+str(page_link))
            # print(link_to_page)
            r = requests.get(link_to_page)
            c = r.content
            soup = BeautifulSoup(c, "html.parser")
            all = soup.find_all("div", {"class": "job-data"})
            for job_data in all:
                links_to_job = job_data.find_all(href=re.compile("Zaposlitev"))
                for link_to_job in links_to_job:
                    d = {}
                    r = requests.get(link_to_job["href"])
                    c = r.content
                    soup = BeautifulSoup(c, "html.parser")
                    d["Title"] = soup.find("h1").text.replace("\t", "").replace("\n", "")
                    deadline = soup.find(id="deadline")
                    d["Application_date"] = form_date(deadline.find("time").text.replace("\t", "").replace("\n", ""))
                    d["Place_of_work"] = soup.find("p", "job-location").text
                    d["Company"] = soup.find("li", "job-company").text
                    d["Url"] = link_to_job["href"]
                    try:
                        d["Description"] = form_text(soup.find(id="job-description").text)
                    except AttributeError:
                        d["Description"] = "/"
                    published = soup.find(id="published")
                    d["Date_of_announcement"] = form_date(published.find("time").text)
                    d["Region"] = name_of_region
                    d["Site"] = "deloglasnik.si"
                    #print(d)
                    #print("-----------------------------")
                    list_of_dics.append(d)

    df = DataFrame(list_of_dics)

    df.to_csv("ScraperData/deloglasnik.csv", index=False)
    print("Deloglasnik končan!")
    print("število zadetkov: " + str(len(list_of_dics)))
    print("--------------------------------------")