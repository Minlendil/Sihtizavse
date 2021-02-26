from flask import Flask, render_template, request
import csv
from re import sub
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from pandas import DataFrame

app = Flask(__name__)


def findmatch(title_string, input_word):
    wordList = sub("[^\w]", " ", title_string).split()
    for x in wordList:
        match_procent = SequenceMatcher(None, x, input_word).ratio()
        if match_procent > 0.74:
            return True


def date_compare(days_delta, row_date):
    cutoff_date = datetime.today() - timedelta(days=days_delta)
    date_time_obj = datetime.strptime(row_date, '%d.%m.%Y')
    return cutoff_date <= date_time_obj


def sites_checked(sites):
    list_of_site_drops = []
    if "1" not in sites:
        list_of_site_drops.append("deloglasnik.si")
    if "2" not in sites:
        list_of_site_drops.append("optius.com")
    if "3" not in sites:
        list_of_site_drops.append("mojedelo.com")
    if "4" not in sites:
        list_of_site_drops.append("zaposlitev.info")
    if "5" not in sites:
        list_of_site_drops.append("iskanjedela.si")
    return list_of_site_drops

@app.route("/")
def first_page():
    # local pathway
    with open('Data/MainDataset.csv', encoding="utf8") as data:
    # deployment pathway
    # with open('var/www/Sihtizavse/Sihtizavse/Data/MainDataset.csv', encoding="utf8") as data:
        count = 0
        places = []
        for row in csv.DictReader(data):
            if len(places) < 100:
                places.append(row)
            else:
                break
        count = len(places)
    with open("Data/datum.txt") as datum_osvezitve:
        datum = datum_osvezitve.read()
    return render_template("first_page.html", places=places, count=count, datum=datum)


@app.route("/search", methods=["GET", "POST"])
def index():
    datum_ticked = {"1": "", "3": "", "7": "", "30": ""}
    sites_ticked = {"1": "checked", "2": "checked", "3": "checked", "4": "checked", "5": "checked"}
    regions_ticked = {"Gorenjska": "", "Goriška": "", "Jugovzhodna Slovenija": "", "Koroška": "", "Obalno-kraška": "",
                      "Osrednjeslovenska": "", "Podravska": "", "Pomurska": "", "Posavska": "",
                      "Primorsko-notranjska": "", "Savinjska": "", "Zasavska": "", "Tujina": ""}
    with open("Data/datum.txt") as datum_osvezitve:
        datum = datum_osvezitve.read()
    # local pathway
    with open('Data/MainDataset.csv', encoding="utf8") as data:
    # deployment pathway
    # with open('var/www/Sihtizavse/Sihtizavse/Data/MainDataset.csv', encoding="utf8") as data:
        count = 0
        places = []
        a_kraj = ""
        a_regions = "Regije: Vse"
        a_key_word = ""
        a_date = ""
        izberi_regijo = "Izberi regijo"

        if request.method == "POST":
            regions = request.form.getlist("regions")
            kraj = request.form.get("city")
            key_word = request.form.get("key_word")
            date = request.form.get("date")
            sites = request.form.getlist("sites")

            # ticks the form inputs that were used in last search
            if date is not None:
                datum_ticked[date] = "checked"

            if regions is not None:
                for region in regions:
                    regions_ticked[region] = "checked"

            if len(sites) != 5:
                for k in sites_ticked:
                    if k not in sites:
                        sites_ticked[k] = ""

            # Zamenja napis "Izberi regijo" z imenom izbrano regijo:
            if len(regions) == 0:
                izberi_regijo = "Izberi regijo"
            elif len(regions) == 1:
                izberi_regijo = regions[0]
            else:
                izberi_regijo = regions[0] + ", ..."
            # preveri, da zapis ni dolg več kot 20 znakov-zaradi page aligmenta
            if len(izberi_regijo) > 20:
                izberi_regijo = izberi_regijo[:17] +"..."


            # Za prikaz iskanih polj pod iskalnikom:
            if len(regions) == 0:
                a_regions = "Regije: Vse"
            else:
                a_regions = "Regije: "
                for x in regions:
                    if x == regions[-1]:
                        a_regions += x + ' '
                    else:
                        a_regions += x + ', '
            if len(kraj) == 0:
                a_kraj = ""
            else:
                a_kraj = "| Kraj: " + kraj

            if len(key_word) == 0:
                a_key_word = ""
            else:
                a_key_word = "| Ključna beseda: " + key_word

            if date is None:
                a_date = ""
            elif date == "1":
                a_date = "| Danes"
            elif date == "3":
                a_date = "| Zadnje 3 dni"
            elif date == "7":
                a_date = "| Pretekli teden"
            elif date == "30":
                a_date = "| Pretekli mesec"

            # iskalna logika searchbara
            for row in csv.DictReader(data):
                if len(regions) == 0:
                    if len(kraj) == 0:
                        if len(key_word) == 0:
                            places.append(row)
                        elif (key_word.lower() in row["Description"].lower()) or (
                                findmatch(row["Title"].lower(), key_word.lower()) == True):
                            places.append(row)
                    elif row["Place_of_work"].lower() == kraj.lower():
                        if len(key_word) == 0:
                            places.append(row)
                        elif (key_word.lower() in row["Description"].lower()) or (
                                findmatch(row["Title"].lower(), key_word.lower()) == True):
                            places.append(row)
                elif row["Region"] in regions:
                    if len(kraj) == 0:
                        if len(key_word) == 0:
                            places.append(row)
                        elif (key_word.lower() in row["Description"].lower()) or (
                                findmatch(row["Title"].lower(), key_word.lower()) == True):
                            places.append(row)
                    elif row["Place_of_work"].lower() == kraj.lower():
                        if len(key_word) == 0:
                            places.append(row)
                        elif (key_word.lower() in row["Description"].lower()) or (
                                findmatch(row["Title"].lower(), key_word.lower()) == True):
                            places.append(row)

            # nastavitev datuma iskanja
            new_places = []
            for row in places:
                if date is None:
                    break
                elif date_compare(int(date), row["Date_of_announcement"]) == True:
                    new_places.append(row)
            if date is not None:
                places = new_places

            # nastavitev strani po katerih želi uporabnik iskati
            if len(sites) != 5:
                list_to_check = sites_checked(sites)
                df = DataFrame(places)
                df = df[~df["Site"].isin(list_to_check)]
                places = df.to_dict('records')

        else:
            for row in csv.DictReader(data):
                places.append(row)

        count = len(places)

    # začasna rešitev, preden se lotim paganation nardit - zmanjša prikaz zadetkov na 300
    if len(places) > 1000:
        places = places[:500]
        count = len(places)

    return render_template("search_output.html", places=places, count=count, regions=a_regions, kraj=a_kraj,
                           key_word=a_key_word, date=a_date, datum_ticked=datum_ticked, regions_ticked=regions_ticked,
                           sites_ticked=sites_ticked, izberi_regijo=izberi_regijo, datum=datum)


if __name__ == "__main__":
    app.run(debug=True)