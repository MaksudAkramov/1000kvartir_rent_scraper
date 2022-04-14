import os
import re
import json

from time import sleep
from random import randint

from db import collection


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from dotenv import load_dotenv

load_dotenv()


class Scrape():

    def scrapedata(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("window-size=1200x600")
        driver = webdriver.Chrome(os.environ['CHROMEDRIVER_PATH'], service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://www.1000kvartir.uz/mr/rent?page=1')

        while True:
            try:
                next_page = driver.find_element_by_link_text('»')
                offers = driver.find_elements_by_css_selector('a.desc-place__more-info')
                data = get_data(driver, offers)
                click_button(driver, next_page)
                sleep(randint(1, 5))
                continue
            except: 
                sleep(randint(1, 5))
                last_page = driver.find_element_by_css_selector('li.next.disabled') 
                offers = driver.find_elements_by_css_selector('a.desc-place__more-info')
                data = get_data(driver, offers)
                break 
        driver.quit() 


def close_window(driver, parent):
    driver.close()
    driver.switch_to.window(parent)
    sleep(randint(1, 5))


def click_button(driver, button):
    driver.implicitly_wait(10)
    ActionChains(driver).move_to_element(button).click(button).perform()


def get_data(driver, offers):
    for offer in offers:
        click_button(driver, offer)
        sleep(randint(1, 5))
        parent = driver.window_handles[0]
        chld = driver.window_handles[1]
        driver.switch_to.window(chld)

        link_of_offer = driver.current_url
        h3s = driver.find_elements_by_tag_name('h3')
        number_of_rooms = driver.find_elements_by_xpath("//*[contains(text(), 'Кол-во комнат')]")[1].text
        number_of_rooms = int(re.search(r'\d+', number_of_rooms).group())
        level_and_number_of_levels = driver.find_elements_by_xpath("//*[contains(text(), 'Этаж/Кол-во этажей')]")[0].text
        level = int(re.search(r'\d+', level_and_number_of_levels).group())
        area = driver.find_elements_by_xpath("//*[contains(text(), 'Площадь (Общ./Жил./Кух.) ')]")[0].text
        area = int(re.search(r'\d+', area).group())
        type_of_apartment = driver.find_elements_by_xpath("//*[contains(text(), 'Тип дома')]")[0].text
        type_of_apartment = type_of_apartment.splitlines()[1]
        length_of_stay = driver.find_elements_by_xpath("//*[contains(text(), 'Срок аренды ')]")[0].text
        length_of_stay = length_of_stay.splitlines()[1]
        list_of_images = []
        all_images = {'images': list_of_images}
        main_image = driver.find_element_by_id('main-image').get_attribute('src')
        small_images = driver.find_elements_by_class_name('small-image')

        additional_info_table = driver.find_elements_by_css_selector('ul.additional-information__list')
        facilities1 = additional_info_table[0].find_elements_by_tag_name('li')
        facilities2 = additional_info_table[1].find_elements_by_tag_name('li')


        facility_list = []
        for facility in facilities1:
            facility_list.append(facility.text)
        for facility in facilities2:
            facility_list.append(facility.text)    

        price = driver.find_element_by_class_name('price').text
        price_in_usd = price.splitlines()[0]
        price_in_sum = price.splitlines()[1]
        date = driver.find_element_by_tag_name('p').text
        district = driver.find_element_by_css_selector('div.placeholder').text
        address = h3s[1].text + ', ' + district
        description =  driver.find_element_by_css_selector('div.detailed-description').text

        if description == 'Описание:\nОписание отсутствует':
            description = description.splitlines()[1]
        else:
            description = description.replace('Описание:', '')
            description = description.replace('\n', ' ')    
        
        list_of_images.append(main_image)
        for img in small_images:
            img_link = img.get_attribute('href')
            list_of_images.append(img_link)  

        overall_data = {
            'src': link_of_offer,
            'main_info': {
                'address': address,
                'area in m^2': area,
                'number of rooms': number_of_rooms,
                'level': level,
                'price in usd': price_in_usd,
                'type of apartment': type_of_apartment,
                'preffered lenght of stay': length_of_stay,
                'date&time posted': date,
                'description': description,
                'additional facilities': facility_list,
                'images': list_of_images
            }
        }    
        
        if collection.count_documents({'src': link_of_offer}) == 0:
            collection.insert_one(overall_data)
            close_window(driver, parent)  
        else:
            close_window(driver, parent)
    


data = Scrape()



if __name__ == "__main__":
    data.scrapedata()