import requests
import re
import time
import concurrent.futures
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def log_debug(message):
    """ Scrie mesajele de debugging într-un fișier text """
    with open("debug_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def search_product(query):
    """ Caută un produs folosind SerpAPI și obține linkurile către magazine """
    api_key = "ea6b45bcc8887da0b4c0aacb646fde0eea09cc2e950cf21c3408d795abc81bfb"
    search_url = f"https://serpapi.com/search.json?q={query}&api_key={api_key}&gl=MD"

    try:
        response = requests.get(search_url, timeout=5)
        if response.status_code != 200:
            log_debug(f"Eroare la API: {response.status_code}")
            return []

        results = response.json()
    except requests.exceptions.RequestException as e:
        log_debug(f"Eroare la conectarea la API: {e}")
        return []

    products = []
    for result in results.get('organic_results', []):
        name = result.get('title', 'No title')
        link = result.get('link', '#')
        description = result.get('snippet', 'No description')

        # ✅ Excludem imaginea din API și o luăm direct de pe site
        image_url = get_image_from_page(link)

        if not image_url:
            log_debug(f"⚠️ Imagine lipsă pentru {name}, folosim placeholder.")
        image_url = "/static/img/placeholder.png"




        # ✅ Dacă nici pe site nu există o imagine validă, folosește un placeholder
        if not image_url:
            image_url = "/static/img/placeholder.png"

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


def get_image_from_page(link):
    """Încearcă să extragă imaginea produsului de pe pagina magazinului"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://google.com"  # Unii furnizori blochează accesul fără referer
    }

    img = None  # Inițializăm variabila img

    try:
        response = requests.get(link, headers=headers, timeout=5)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "lxml")

        # 🔹 Ultra.md
        if "ultra.md" in link:
            img = soup.select_one("img.show.product-image")

        # 🔹 Darwin.md
        elif "darwin.md" in link:
            img = soup.select_one("img.open-img.lazy-image.lazy-loaded")
            if not img:
                img = soup.select_one("div.product-img.lazy-image img")
                if img:
                    return img.get("data-src") or img.get("src")

        # 🔹 Enter.online
        elif "enter.online" in link:
            img = soup.select_one("img.open_img")
            if not img:
                link_tag = soup.select_one("a[data-caption]")
                if link_tag:
                    return link_tag.get("href")

        # 🔹 Moldcell.md
        elif "moldcell.md" in link:
            img = soup.select_one("img[src*='Phones']")

        # 🔹 Amazon, eMAG, Altex, PC Garage, Asus Store
        elif any(domain in link for domain in ["amazon.", "emag.", "altex.", "pcgarage.", "asus.com"]):
            img = soup.select_one("img[src*='product']")  # Verificăm imagini de produs

        # ✅ Verificăm dacă imaginea există și returnăm URL-ul
        if img and img.get("src"):
            image_url = img["src"]
            if image_url.startswith("//"):
                image_url = "https:" + image_url  # Adăugăm protocolul
            return image_url
        print(f"🔎 Test imagine pentru {link}: {image_url}")


        return None  # Dacă nu s-a găsit imaginea

    except Exception as e:
        print(f"❌ Eroare la parsarea imaginii pentru {link}: {e}")
        return None


import json

def get_price_from_link(link):
    """Obține prețul produsului, încercând atât BeautifulSoup, cât și JSON dacă este necesar."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(link, headers=headers, timeout=5)
        if response.status_code != 200:
            log_debug(f"Eroare la accesarea paginii: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "lxml")

        # 🔹 Verificăm mai multe selectoare pentru preț
        price_selectors = [
            "span.price", "div.price", "span.price-new",
            "div.product-price", "span.regular-price",
            "h2.price", "p.price", "span[class*='price']",
            "div[class*='price']", "span[class*='amount']",
            "div[class*='amount']", "span[data-price]",
            "span[class*='text-blue']",
            "span[class*='discount']",
            "div[class*='final-price']",
            "span[data-price]",
            "span[class*='current-price']",
            "span[class*='product-price']"
        ]

        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                raw_price = element.get_text(strip=True)
                extracted_price = extract_price(raw_price)
                if extracted_price:
                    return extracted_price

        # 🔹 Dacă prețul nu este în HTML, verificăm dacă există în JSON
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string)
                if "offers" in data and "price" in data["offers"]:
                    return float(data["offers"]["price"])
            except json.JSONDecodeError:
                continue

        log_debug("⚠️ Nu s-a găsit prețul pe pagină.")
        return None

    except Exception as e:
        log_debug(f"❌ Eroare la parsarea paginii: {e}")
        return None





def extract_price(text):
    """ Extrage un preț numeric dintr-un text folosind regex și conversii """
    pattern = r'(\d{1,3}(?:[\s,.]?\d{3})*(?:[\.,]\d{2})?)\s*(MDL|lei|RON|€|\$)?'
    matches = re.findall(pattern, text)
    if matches:
        price = matches[0][0].replace(",", ".").replace(" ", "").replace(" ", "")
        return float(price)
    return None


def fetch_price(url):
    """ Obține prețul unui produs și introduce o mică pauză pentru a evita rate limiting """
    time.sleep(1)  # Pauză de 1 secundă între request-uri
    price = get_price_from_link(url)
    return {"url": url, "price": price}

def search_product_parallel(urls):
    """ Caută produsele pe mai multe site-uri în paralel folosind ThreadPoolExecutor """
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(fetch_price, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            result = future.result()
            if result["price"]:
                results.append(result)
    return results




