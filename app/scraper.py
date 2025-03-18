import requests
import re
import time
import concurrent.futures
from bs4 import BeautifulSoup

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

        # ✅ Încearcă să preiei imaginea din SerpAPI
        image_url = result.get('thumbnail', None)

        # ✅ Dacă SerpAPI nu furnizează o imagine validă, încearcă să extragi imaginea de pe site
        if not image_url or "placeholder" in image_url or image_url == "#":
            log_debug(f"⚠️ Imagine lipsă pentru {name}. Se încearcă extragerea de pe pagină...")
            image_url = get_image_from_page(link)

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
    """ Încearcă să extragă imaginea produsului direct de pe site folosind BeautifulSoup """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(link, headers=headers, timeout=5)
        if response.status_code != 200:
            log_debug(f"❌ Eroare la accesarea paginii pentru imagine: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "lxml")

        # 🔹 Lista de posibile selectoare CSS pentru imagini
        image_selectors = [
            "meta[property='og:image']",  # Unele site-uri folosesc Open Graph
            "meta[name='twitter:image']",
            "img.product-image",
            "div.product img",
            "figure img",
            "img.main-image",
            "img[src*='product']",
        ]

        for selector in image_selectors:
            element = soup.select_one(selector)
            if element:
                # Dacă este un meta tag, extrage conținutul
                image_url = element["content"] if "content" in element.attrs else element["src"]
                if image_url.startswith("//"):
                    image_url = "https:" + image_url
                return image_url

        log_debug("⚠️ Nu s-a găsit o imagine validă pe pagină.")
        return None

    except Exception as e:
        log_debug(f"❌ Eroare la parsarea paginii pentru imagine: {e}")
        return None

def get_price_from_link(link):
    """ Obține prețul de pe site folosind BeautifulSoup """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(link, headers=headers, timeout=5)
        if response.status_code != 200:
            log_debug(f"Eroare la accesarea paginii: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "lxml")
        
        # 🔹 Lista de posibile selectoare CSS pentru preț (fără `p.text-[20px]`)
        price_elements = [
            "span.price-new",
            "div.price-new",
            "span.grid-price",
            "div.product-price",
            "span.regular",
            "div.custom_product_price",
            "span.text-blue.relative.mb-2.text-4xl.font-bold", # Ultra.md
            "span[class*='text-blue']",  # Ultra.md (fallback)
            "div.custom_product_price span.regular",   # Smart.md
            "div.price-head2.red h2",  # Moldcell.md
        ]

        for selector in price_elements:
            element = soup.select_one(selector)
            if element:
                raw_price = element.get_text(strip=True)
                extracted_price = extract_price(raw_price)
                if extracted_price:
                    return extracted_price

        log_debug("⚠️ Nu s-a găsit prețul pe pagină.")
        return None

    except Exception as e:
        log_debug(f"❌ Eroare la parsarea paginii: {e}")
        return None

def extract_price(text):
    """ Extrage un preț numeric dintr-un text folosind regex """
    pattern = r'(\d{1,3}(?:[\s,.]?\d{3})*(?:[\.,]\d{2})?)\s*(MDL|lei|RON|€|\$)?'
    matches = re.findall(pattern, text)
    if matches:
        price = matches[0][0].replace(",", ".").replace(" ", "")
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
