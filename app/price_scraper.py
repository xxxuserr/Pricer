from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import re

def extract_price(text):
    """
    Funcție care extrage un preț dintr-un text folosind regex îmbunătățit.
    """
    pattern = r'(\d{1,3}(?:[\s,.]?\d{3})*(?:[\.,]\d{2})?)\s*(MDL|lei|RON|€|\$)'
    
    matches = re.findall(pattern, text)
    if matches:
        price = matches[0][0].replace(",", ".").replace(" ", "")
        return float(price)
    
    return None

def get_price_from_link_selenium(link):
    """ Extragere preț cu Selenium pentru pagini care încarcă datele dinamic. """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(link)
        time.sleep(5)  # Așteptăm să se încarce pagina complet

        # 🔍 Verificăm mai multe clase posibile unde poate fi prețul
        price_selectors = [
            "//p[contains(@class, 'regular')]",  
            "//div[contains(@class, 'custom_product_price')]",
            "//span[contains(@class, 'text-blue') and contains(@class, 'font-bold')]",  # Ultra.md
            "//span[contains(text(), 'lei')]"  
        ]

        for selector in price_selectors:
            try:
                price_element = driver.find_element(By.XPATH, selector)
                price_text = price_element.text.strip()
                extracted_price = extract_price(price_text)
                if extracted_price:
                    driver.quit()
                    return extracted_price
            except:
                continue  

        driver.quit()
        return None

    except Exception as e:
        print(f"Eroare Selenium: {e}")
        driver.quit()
        return None

# 🔥 Testare
#url = "https://ultra.md/product/s928-s24-ultra-12512gb-black"
#print(f"Preț extras: {get_price_from_link_selenium(url)} lei")
