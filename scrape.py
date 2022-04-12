import re
import json

from time import sleep
from random import randint

from db import collection


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager


class Scrape():

    def scrapedata(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(executable_path="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://www.1000kvartir.uz/mr/rent?page=1')

        while True:
            try:
                next_page = driver.find_element_by_link_text('»')
                offers = driver.find_elements_by_css_selector('a.desc-place__more-info')
                data = get_data(driver, offers)
                next_page.click()
                sleep(randint(1, 5))
                continue
            except: 
                sleep(randint(1, 5))
                last_page = driver.find_element_by_css_selector('li.next.disabled') 
                offers = driver.find_elements_by_css_selector('a.desc-place__more-info')
                data = get_data(driver, offers)
                break
          
        driver.quit() 

def get_data(driver, offers):
    for offer in offers:
        offer.click()
        sleep(randint(1, 5))
        parent = driver.window_handles[0]
        chld = driver.window_handles[1]
        driver.switch_to.window(chld)

        link_of_offer = driver.current_url
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
                'area in m^2': area,
                'number of rooms': number_of_rooms,
                'level': level,
                'price in usd': price_in_usd,
                'type of apartment': type_of_apartment,
                'preffered lenght of stay': length_of_stay,
                'date&time posted': date,
                'district': district,
                'description': description,
                'additional facilities': facility_list,
                'images': list_of_images
            }
        }    

        collection.insert_one(overall_data)
        
        driver.close()
        driver.switch_to.window(parent)
        sleep(randint(1, 5)) 
            

data = Scrape()



if __name__ == "__main__":
    data.scrapedata()