import requests
import re
from bs4 import BeautifulSoup
from app.price_scraper import get_price_from_link_selenium


def log_debug(message):
    with open("debug_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def search_product(query):
    api_key = "ea6b45bcc8887da0b4c0aacb646fde0eea09cc2e950cf21c3408d795abc81bfb"
    search_url = f"https://serpapi.com/search.json?q={query}&api_key={api_key}&gl=MD"
    
    try:
        response = requests.get(search_url)
        if response.status_code != 200:
            log_debug(f"Eroare la API: {response.status_code}")
            return []

        results = response.json()
        for result in results.get('organic_results', []):
            log_debug(f"\n Analiză produs: {result}")
        for result in results.get('shopping_results', []):
            log_debug(f"\n Analiză produs(SHOPPING): {result}")
    except requests.exceptions.RequestException as e:
        log_debug(f"Eroare la conectarea la API: {e}")
        return []
    
    products = []
    for result in results.get('organic_results', []):
        name = result.get('title', 'No title')
        link = result.get('link', '#')
        description = result.get('snippet', 'No description')
        image_url = result.get('thumbnail', '#')
        
        product_details = {
            'name': name,
            'link': link,
            'description': description,
            'image_url': image_url,
        }

        if link != '#':
            price = get_price_from_link(link)
            if price:
                product_details['price'] = price

        products.append(product_details)
    
    return products

def get_price_from_link(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(link, headers=headers, timeout=10)
        if response.status_code != 200:
            log_debug(f"Eroare la accesarea paginii: {response.status_code}")
            return get_price_from_link_selenium(link)  # Trecem la Selenium dacă requestul eșuează

        soup = BeautifulSoup(response.text, "lxml")
        
        # 🔹 Caută prețul în clasele specifice ale site-urilor
        price_elements = [
            "span.price-new",  
            "div.price-new",   
            "span.grid-price", 
            "div.product-price",
            "span.regular",     
            "div.custom_product_price",
            "p.text-[20px]",  # Adăugat pentru noul site
        ]

        for selector in price_elements:
            element = soup.select_one(selector)
            if element:
                raw_price = element.get_text(strip=True)
                extracted_price = extract_price(raw_price)
                if extracted_price:
                    return extracted_price

        # 🔹 Dacă nu găsește nimic în elementele CSS, folosim Selenium
        return get_price_from_link_selenium(link)
    
    except Exception as e:
        log_debug(f"Eroare la parsarea paginii: {e}")
        return None

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

#  Testare pe un URL de produs
#if __name__ == "__main__":
#   test_url = "https://www.smart.md/apple-iphone-15-pro-max-256gb-blue-titanium"
#    price = get_price_from_link(test_url)
#    print(f"Preț extras: {price} lei")