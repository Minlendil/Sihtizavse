from zaposlitev_bs4 import zaposlitev
from optius_bs4 import optius
from deloglasnik_bs4 import deloglasnik
from iskanjedela import iskanjedela
from mojedelo_bs4 import mojedelo
from time import sleep
import schedule
import pandas as pd
import logging
from datetime import datetime

# trenutne spletne strani:
"""
deloglasnik.si      bs4
mojedelo.com        bs4
optius.com          bs4
zaposlitev.info     bs4
iskanjedela.si      selenium
"""

logging.basicConfig(filename="main_scraper.log", level=logging.WARNING)


def main():
    try:
        optius()
    except Exception as e:
        logging.exception(str(e))
    try:
        zaposlitev()
    except Exception as e:
        logging.exception(str(e))
    try:
        deloglasnik()
    except Exception as e:
        logging.exception(str(e))
    try:
        iskanjedela()
    except Exception as e:
        logging.exception(str(e))
    try:
        mojedelo()
    except Exception as e:
        logging.exception(str(e))

    df_optius = pd.read_csv("ScraperData/optius.csv")
    df_zaposlitev = pd.read_csv("ScraperData/zaposlitev.csv")
    df_deloglasnik = pd.read_csv("ScraperData/deloglasnik.csv")
    df_iskanjedela = pd.read_csv("ScraperData/iskanjedela.csv")
    df_mojedelo = pd.read_csv("ScraperData/mojedelo.csv")

    MainDataset = pd.concat([df_optius, df_zaposlitev, df_deloglasnik, df_mojedelo, df_iskanjedela], ignore_index=True)
    MainDataset = MainDataset.drop_duplicates(subset=["Title", "Company", "Place_of_work"])
    MainDataset = MainDataset.sample(frac=1).reset_index(drop=True)
    MainDataset.to_csv("Data/MainDataset.csv")

    print("finished output")
    print("Stevilo delovnih mest " + str(len(MainDataset)))

    with open("Data/datum.txt", "w") as datum:
        today = datetime.today().strftime("%d.%m.%Y %H:%M")
        datum.write(today)


# iskanjedela je odstranjeno, ker porabi preveč časa in RAMa
def secondary():

    try:
        optius()
    except Exception as e:
        logging.exception(str(e))
    try:
        zaposlitev()
    except Exception as e:
        logging.exception(str(e))
    try:
        deloglasnik()
    except Exception as e:
        logging.exception(str(e))
    try:
        mojedelo()
    except Exception as e:
        logging.exception(str(e))

    df_optius = pd.read_csv("ScraperData/optius.csv")
    df_zaposlitev = pd.read_csv("ScraperData/zaposlitev.csv")
    df_deloglasnik = pd.read_csv("ScraperData/deloglasnik.csv")
    df_iskanjedela = pd.read_csv("ScraperData/iskanjedela.csv")
    df_mojedelo = pd.read_csv("ScraperData/mojedelo.csv")

    MainDataset = pd.concat([df_optius, df_zaposlitev, df_deloglasnik, df_mojedelo, df_iskanjedela], ignore_index=True)
    MainDataset = MainDataset.drop_duplicates(subset=["Title", "Company", "Place_of_work"])
    MainDataset = MainDataset.sample(frac=1).reset_index(drop=True)
    MainDataset.to_csv("Data/MainDataset.csv")
    print("finished output")
    print("Stevilo delovnih mest " + str(len(MainDataset)))

    with open("Data/datum.txt", "w") as datum:
        today = datetime.today().strftime("%d.%m.%Y %H:%M")
        datum.write(today)


schedule.every().day.at("08:00").do(main)
schedule.every().day.at("15:30").do(secondary)
schedule.every().day.at("22:00").do(main)

while True:
    schedule.run_pending()
    sleep(1)

