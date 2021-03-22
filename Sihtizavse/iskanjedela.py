from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from datetime import date, timedelta, datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pandas import DataFrame, read_csv
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def regije_popravki(name):
    if name == "JugovzhodnaSlovenija":
        return "Jugovzhodna Slovenija"
    else:
        return name


def from_text(something):

    something = something.replace("\n"," ")
    start_position = something.find("Opis del in nalog")
    end_position = something.find("Izobrazba:")
    opis = something[start_position+19:end_position-1]
    if len(opis) <= 250:
        return opis
    else:
        return opis[0:247] + "..."


def iskanjedela():
    list_of_dics = []
    df_bf = read_csv("ScraperData/iskanjedela.csv")

    for index, row in df_bf.iterrows():
        if date.today() - timedelta(days=30) < (datetime.strptime(row["Date_of_announcement"], "%d.%m.%Y")).date():
            list_of_dics.append(row.to_dict())

    opts = Options()
    opts.headless = True
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    action = ActionChains(driver)
    driver.get("https://www.iskanjedela.si")
    driver.set_window_size(1500, 1080)
    driver.implicitly_wait(10)
    # cookie clicker
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@id='cc-approve-button-thissite']"))
        )
        cookie_clicker = driver.find_element_by_xpath("//a[@id='cc-approve-button-thissite']")
        cookie_clicker.send_keys(Keys.RETURN)
    except NoSuchElementException:
        print("No cookie screen")
    regija_button_clicker = driver.find_element_by_xpath("//button[contains(text(), 'Regija')]")
    regija_button_clicker.click()
    List_of_regions = driver.find_elements_by_xpath("//div[@class = 'facet-dropdown__menu py-2 dropdown-menu show']/button")
    regija_button_clicker.click()
    
    count=0
    
    # izberi datum (v drugi vrstici): 0 = danes, 1 = tri dni, 2...
    driver.find_element_by_xpath("//button[contains(text(), 'datum objave')]").click()
    driver.find_elements_by_xpath("//div[@class = 'facet-dropdown__menu py-2 dropdown-menu show']/button")[0].click()
    driver.find_element_by_xpath("//button[contains(text(), 'datum objave')]").click()
        
    for region in List_of_regions:
        if List_of_regions[0] == region:
            regija_button_clicker.click()
            region.click()
            region_name = region.find_element_by_xpath(".//span").text[:-4].replace(" ","").replace("(","")
            regija_button_clicker.click()

        else:
            regija_button_clicker.click()
            List_of_regions[count].click()
            region.click()
            region_name = region.find_element_by_xpath(".//span").text[:-4].replace(" ","").replace("(","")
            #print(region_name)
            #print("--------------")
            regija_button_clicker.click()
            count += 1
        sleep(2)
        
        # scroll down

        driver.find_element_by_xpath("//div[@data-js='search-page__list']").click()
        num_of_results = driver.find_element_by_xpath("//div[@class='card-header bg-white p-3 rounded-0']").text
        num_of_results = int("".join(i for i in num_of_results if i.isdigit()))
        try:
            data = driver.find_element_by_xpath("//div[@class='details-component']")
            row = data.find_elements_by_xpath("//a[@data-test='search-page-item']")

            #print(num_of_results)
            while True:
                if len(row) < num_of_results:
                    action.key_down(Keys.DOWN)
                    action.key_up(Keys.DOWN)
                    action.perform()
                    row = data.find_elements_by_xpath("//a[@data-test='search-page-item']")
                    #print(len(row))
                else:
                    break

            # the start of the data collection on search results

            b = 0

            for a in row:
                d = {}
                a.click()
                # sleep time might be decreased. if not used it skips forward, before the element is loaded properly
                sleep(0.3)
                # this is the place where all the data is collected, that is going to be displayed on your page
                d["Title"] = data.find_element_by_xpath("//h4[@class='mb-4 pt-4 details-component__header w-100']").text
                dates_container = (data.find_element_by_xpath("//ul[@class='list-unstyled details-component__job-sub-info']"))
                d["Application_date"] = dates_container.find_elements_by_xpath(".//li")[1].text[12:]
                d["Place_of_work"] = driver.find_element_by_xpath("//h6[@class='mt-0 details-component__company-location']").text
                d["Company"] = data.find_element_by_xpath("//h6[@class = 'mb-1 details-component__company-name']").text
                d["Url"] = driver.current_url
                d["Description"] = from_text(driver.find_element_by_xpath("//article[@class= 'p-4 bg-white pb-3 container']").text)
                d["Date_of_announcement"] = dates_container.find_elements_by_xpath(".//li")[0].text[14:].replace(" ","")
                d["Region"] = region_name
                d["Site"] = "iskanjedela.si"
                b += 1
                list_of_dics.append(d)
            print(b)
        except NoSuchElementException:
            continue

    df = DataFrame(list_of_dics)
    df["Region"] = df["Region"].apply(regije_popravki)
    df = df.drop_duplicates(subset=["Title", "Company", "Place_of_work"])
    df.to_csv("ScraperData/iskanjedela.csv", index = False)
    driver.quit()
    print("iskanjedela končan!")
    print("število zadetkov: " + str(len(df)))
    print("--------------------------------------")


if __name__ == "__main__":
    iskanjedela()
