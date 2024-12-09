from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from random_user_agent.user_agent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from plyer import notification
import requests
import time
import easyocr
import os
from PIL import Image
import time
import csv
class AmazonPriceTracker:
    def __init__(self):
        self.driver = self.driver_setup()
        self.current_price = None
        self.product_title = None
    def driver_setup(self):        
        options = webdriver.ChromeOptions()
        # options.add_experimental_option("detach", True)
        ua = UserAgent()
        options.add_argument("--headless")
        user_agent = ua.get_random_user_agent()
        # options.add_argument(f"--user-agent={user_agent}")
        driver = webdriver.Chrome(options=options)
        return driver
    
    def captcha_solver(self):
        reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory
        result = reader.readtext('captcha.png')
        for detection in result:
            self.extracted_text = (detection[1])
        return self.extracted_text
    
    def track_price(self, product_url,max_retries=3):
        self.driver.get(product_url)
        try:
            for attempt in range(max_retries):
                captcha_image = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//img[contains(@src, 'captcha')]")))
                image_url = captcha_image.get_attribute("src")
                response = requests.get(image_url)
                if response.status_code == 200:
                    with open('captcha.png', 'wb') as f:
                        f.write(response.content)
                    print("Image Download Succesfully")
                else:
                    print("Image Download Failed")    
                self.captcha_solver()    
                captcha_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "captchacharacters")))
                captcha_input.send_keys(self.extracted_text)
                time.sleep(1)
                    # Submit_Btn Click
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "a-button-text"))).click()
                print("Captcha Solved Successfully")
                return True
            print(f"Captcha Not Solved after {max_retries} attempts")
            return False
        except Exception as e:
            print(f"Captcha Not Required")
        self.current_price = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "a-price-whole"))).text
        self.product_title = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "productTitle"))).text 
        self.short_product_title = self.product_title[:35]
        self.set_price_alert(149)
        # self.send_notification(self.current_price,short_product_title)
    def send_notification(self, current_price, product_title):
        notification.notify(
            title = f"Amazon Price Tracker - {product_title}",
            message = (f"The Current Price is: {current_price}$"),
            timeout = 10
            )
    def multiple_products(self,file_path):
        with open(file_path,"r") as f:
            for line in f:
                product_url = line.strip()
                self.track_price(product_url)
                self.save_price_history(self.current_price,self.product_title)
    
    def save_price_history(self, current_price, product_title):
        # Save the price history
        with open("price_history.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), product_title, current_price])
            f.close()
            
    def set_price_alert(self,target_price):
        price = self.current_price
        if  (int(price) <= int(target_price)):
            self.send_notification(price,self.product_title[:35])
            # print(f"Price of {self.product_title} is below the target price of {target_price}$")
        
if __name__ == "__main__":
    tracker = AmazonPriceTracker()
    while(True):
        # tracker.track_price(product_url)
        tracker.multiple_products("products.txt")
        time.sleep(60)