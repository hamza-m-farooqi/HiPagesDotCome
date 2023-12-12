from selenium import webdriver
from selenium.webdriver.common.by import By
from config import CATEGORIES,DRIVER
import csv
import time
import logging
import os
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

base_url="https://hipages.com.au"

def initialize_driver():
    if DRIVER=="Edge":
        return webdriver.Edge()
    else:
        return webdriver.Chrome()

def check_and_update_string(input_string, json_file_path='bathroom_renovations.json'):
    try:
        # Check if the JSON file exists
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                
            # Check if the input string exists in the list
            if input_string in data['strings']:
                return True
            else:
                # Append the input string to the list
                data['strings'].append(input_string)
                with open(json_file_path, 'w') as file:
                    json.dump(data, file, indent=2)
                return False
        else:
            # Create a new JSON file with the input string
            data = {'strings': [input_string]}
            with open(json_file_path, 'w') as file:
                json.dump(data, file, indent=2)
            return False
    except Exception as e:
        # Handle any exceptions and return False
        print(f"An error occurred: {e}")
        return False

def update_data_in_json_file(json_data,json_file):
    try:
        json_file=f"{json_file}.json"
        # Check if the JSON file exists
        if os.path.exists(json_file):
            with open(json_file, 'r') as file:
                data = json.load(file)
                data['data'].append(json_data)
                with open(json_file, 'w') as file:
                    json.dump(data, file, indent=2)
                return False
        else:
            # Create a new JSON file with the input string
            data = {'data': [json_data]}
            with open(json_file, 'w') as file:
                json.dump(data, file, indent=2)
            return False
    except Exception as e:
        # Handle any exceptions and return False
        print(f"An error occurred: {e}")
        return False

def scrape_locations_by_category(category_page_url):
    locations_list=[]
    category_page_url=f"{base_url}/find/{category_page_url}"
    driver.get(category_page_url)
    time.sleep(3)
    locations_container_div=driver.find_elements(By.CLASS_NAME,"sc-cCsOjp")[0]
    locations_li_elements=locations_container_div.find_element(By.TAG_NAME,"ul").find_elements(By.TAG_NAME,"li")
    for location_li in locations_li_elements:
        a_tag=location_li.find_element(By.TAG_NAME,"a")
        location_name=a_tag.text
        location_link=a_tag.get_attribute("href")
        locations_list.append({"name":location_name,"link":location_link})
    return locations_list

def is_view_more_present():
    try:
        # Find elements with the text "View More"
        view_more_elements = driver.find_elements(By.XPATH, '//*[contains(text(), "View More")]')
        
        # If at least one element is found, return True
        return (bool(view_more_elements),view_more_elements)
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def click_on_view_more():
    max_attempts = 500
    for _ in range(max_attempts):
        time.sleep(1.5)
        view_more_button_status, view_more_buttons = is_view_more_present()

        if not view_more_button_status:
            print("View More button found. Exiting loop.")
            break

        if view_more_buttons:
            try:
                view_more_buttons[0].click()
                print("Clicked 'View More' button.")
            except Exception as e:
                print(f"Error clicking 'View More' button: {e}")
        time.sleep(1)
    else:
        print("Reached the maximum number of attempts. Exiting loop.")

def scrape_tradies():
    tradies_links=[]
    tradie_cards=driver.find_elements(By.CLASS_NAME,"opus-1wmjk3o")[:-3]
    for tradie_card in tradie_cards:
        link=tradie_card.find_elements(By.TAG_NAME,"a")[0].get_attribute("href")
        tradies_links.append(link)
    suggested_tradie_cards=driver.find_elements(By.CLASS_NAME,"opus-1mu2s8t")
    for tradie_card in suggested_tradie_cards:
        link=tradie_card.find_elements(By.TAG_NAME,"a")[0].get_attribute("href")
        tradies_links.append(link)
    return tradies_links

def scrape_tradie_detail(tradie_detail_link):
    try:
        driver.get(tradie_detail_link)
        time.sleep(2.5)

        tradie_header_info_container = driver.find_element(By.CLASS_NAME, "opus-vwlq1e")
        image = tradie_header_info_container.find_element(By.CLASS_NAME, "opus-117hah9").find_element(By.TAG_NAME, "img").get_attribute("src")
        name = tradie_header_info_container.find_element(By.CLASS_NAME, "opus-19j1v4j").text

        location_and_license_spans = tradie_header_info_container.find_element(By.CLASS_NAME, "opus-1m9uebo").find_elements(By.TAG_NAME, "span")
        location = ""
        license = ""
        try:
            location_element = driver.find_element(By.CLASS_NAME, "opus-15m8f07")
            if location_element is not None:
                location=location_element.text
            license_element = driver.find_element(By.CLASS_NAME, "opus-fsuxi3")
            if license_element is not None:
                license=license_element.text
        except:
            pass
        try:
            phone_number_box = tradie_header_info_container.find_element(By.CLASS_NAME, "phone-number__desktop")
            phone_number_box.click()
        except:
            pass
        time.sleep(2)
        try:
            phone_number = driver.find_element(By.CLASS_NAME, "phone-number__desktop").find_element(By.TAG_NAME, "button").find_elements(By.TAG_NAME, "span")[2].text
        except:
            phone_number="Not Found"
        rating=""
        try:
            rating = driver.find_element(By.CLASS_NAME, "opus-mazxf0").text
        except:
            rating="Not Found"
        try:
            recommendations = driver.find_element(By.CLASS_NAME, "opus-1t2j9bj").text
        except:
            recommendations="Not Found"
        services = ""
        try:
            services_container = driver.find_element(By.ID, "services").find_element(By.CLASS_NAME, "opus-vivbk0")
            services_li_elements = services_container.find_elements(By.TAG_NAME, "li")
        except:
            services="Not Found"
        for services_li_element in services_li_elements:
            services_a_elements = services_li_element.find_elements(By.TAG_NAME, "a")
            for service_element in services_a_elements:
                services += f"{service_element.text} , "
            services_span_elements = services_li_element.find_elements(By.TAG_NAME, "span")
            for service_element in services_span_elements:
                services += f"{service_element.text} , "
        review = ""
        try:
            review_elements = driver.find_elements(By.CLASS_NAME, "opus-gnxoln")
            for review_element in review_elements:
                review += f"{review_element.text} ||| "
        except:
            review="Not Found"

        return {
            "name": name if name else "not found",
            "location": location if location else "not found",
            "rating": rating if rating else "not found",
            "link": tradie_detail_link,
            "image": image if image else "not found",
            "phone": phone_number if phone_number else "not found",
            "licence": license if license else "not found",
            "all_reviews": review if review else "not found",
            "recommendations": recommendations if recommendations else "not found",
            "services": services if services else "not found"
        }
    except Exception as e:
        print(f"An error occurred while scraping tradie details: {e}")
        return None


if __name__ == "__main__":
    driver = initialize_driver()
    

    for category in CATEGORIES:
        locations_list=scrape_locations_by_category(category)
        for i in range(len(locations_list)):
            tradies_detail_by_location=[]
            location=locations_list[i]
            print(f"Going to read {location['name']}\n")
            driver.get(location['link'])
            time.sleep(5)
            click_on_view_more()
            time.sleep(2)
            tradies_link=scrape_tradies()
            for traidie_link in tradies_link:
                if check_and_update_string(traidie_link):
                    continue
                tradies_detail_data=scrape_tradie_detail(traidie_link)
                if tradies_detail_data is not None:
                    update_data_in_json_file(tradies_detail_data,location['name'])
                    tradies_detail_by_location.append(tradies_detail_data)
            # timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            CSV_FILE_PATH=f"{location['name']}.csv"
            with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = tradies_detail_by_location[0].keys() if tradies_detail_by_location else []
                csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write the header
                csv_writer.writeheader()

                # Write the data
                csv_writer.writerows(tradies_detail_by_location)

    logger.info(f"Data has been saved to {CSV_FILE_PATH}")
    driver.quit()
