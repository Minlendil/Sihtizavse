from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
from pandas import DataFrame


def regije_popravki(name):
    if name == "Dolenjska":
        return "Jugovzhodna Slovenija"
    elif name == "Spodnjeposavska":
        return "Posavska"
    elif name == "Obalna":
        return "Obalno-kraška"
    elif name == "Pomurje":
        return "Pomurska"
    else:
        return name


def datum(text):
    dat = {
        "Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4", "Maj": "5", "Jun": "6",
        "Jul": "7", "Avg": "8", "Sep": "9", "Okt": "10", "Nov": "11", "Dec": "12"
    }
    mesec = text[:3]
    trenutni_mesec = datetime.today().strftime("%m")
    if int(dat[mesec]) > int(trenutni_mesec):
        year = datetime.today()-timedelta(days = 365)
        year = year.strftime("%Y")
    else:
        year = datetime.today().strftime("%Y")

    return text[-2:].replace(" ", "") + "." + dat[mesec] + "." + year


def text_trans(opis):
    if len(opis) <= 250:
        return opis
    else:
        return opis[0:247] + "..."


list_of_regions = {2: "Pomurje", 4: "Podravska", 5: "Koroška", 6: "Savinjska", 1: "Zasavska", 9: "Spodnjeposavska",
                 3: "Dolenjska", 12: "Osrednjeslovenska", 7: "Gorenjska", 8: "Notranjsko-kraška",
                 10: "Goriška", 11: "Obalna", 13: "Tujina"}


def zaposlitev():

    base = "https://www.zaposlitev.info/najdi-zaposlitev/"
    base_part2 = "?field_3%5B%5D="
    list_of_dics = []
    for regija_link in range(1, 14):
        name_of_region = list_of_regions[regija_link]
        link_to_site = (base + base_part2 + name_of_region)
        #print(link_to_site)
        #print(name_of_region)
        r = requests.get(link_to_site)
        c = r.content
        soup = BeautifulSoup(c, "html.parser")
        pages = soup.find("div", "wpjb-paginate-links").find_all("a")
        number_of_pages = pages[-2].text
        # print(number_of_pages)
        for page_link in range(1,int(number_of_pages)+1):
            link_to_page = (base + "page/" + str(page_link) +"/"+ base_part2 + name_of_region)
            #print(link_to_page)
            r = requests.get(link_to_page)
            c = r.content
            soup = BeautifulSoup(c, "html.parser")
            jobs = soup.find("div", "wpjb-job-list wpjb-grid").find_all("div", recursive=False)
            # print(jobs)
            for job_data in jobs:
                d = {}
                line_major = job_data.find_all("span","wpjb-line-major")
                d["Title"] = line_major[0].text.replace("\n","")
                d["Application_date"] = "/"
                d["Place_of_work"] = line_major[1].text.replace("\n", "")
                d["Company"] = job_data.find_all("span","wpjb-sub wpjb-sub-small")[0].text
                d["Url"] = line_major[0].find(href=True)["href"]
                try:
                    d["Description"] = text_trans(job_data.find("div", {"style":"width:90%; padding:5em 0 0 9.25em"}).text
                                                  .replace("\n","").replace("\r",""))
                except AttributeError:
                    d["Description"] = "/"
                d["Date_of_announcement"] = datum(line_major[2].text.replace("\n","").replace("\t","").replace(" ",""))
                d["Region"] = regije_popravki(name_of_region)
                d["Site"] = "zaposlitev.info"
                # print(d)
                # print("------------------------------")
                list_of_dics.append(d)

    df = DataFrame(list_of_dics)
    df = df.drop_duplicates(subset=["Title","Company","Place_of_work"])
    df.to_csv("ScraperData/zaposlitev.csv", index=False)
    print("Zaposlitev končan!")
    print("število zadetkov: " + str(len(list_of_dics)))
    print("--------------------------------------")


if __name__ == "__main__":
    zaposlitev()
