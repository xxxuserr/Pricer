import requests
import re
import time
import concurrent.futures
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

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

        image_url = get_image_from_page(link)
        if image_url:
            image_url = download_and_save_image(image_url)
        else:
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
    """Încearcă să extragă imaginea produsului și să o salveze local dacă este blocată"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://google.com"  # Unele site-uri cer Referer valid
    }

    img_url = None  # Inițializează variabila

    try:
        response = requests.get(link, headers=headers, timeout=5)
        if response.status_code != 200:
            return "/static/img/placeholder.png"

        soup = BeautifulSoup(response.text, "lxml")

        # 🔹 Detectăm imaginea produsului
        img = None
        if "ultra.md" in link:
            img = soup.select_one("img.show.product-image")
        elif "darwin.md" in link:
            img = soup.select_one("img.open-img.lazy-image.lazy-loaded")
        elif "enter.online" in link:
            img = soup.select_one("img.open_img")
        elif "moldcell.md" in link:
            img = soup.select_one("img[src*='Phones']")
        elif any(domain in link for domain in ["amazon.", "emag.", "altex.", "pcgarage.", "asus.com"]):
            img = soup.select_one("img[src*='product']")

        if img and img.get("src"):
            img_url = img["src"]
            if img_url.startswith("//"):
                img_url = "https:" + img_url  # Adăugăm protocolul

        # 🔹 Verificăm dacă imaginea este accesibilă
        if img_url and can_access_image(img_url):
            return img_url  # Returnăm URL-ul original dacă este accesibil

        # 🔹 Dacă imaginea este blocată, o descărcăm și o salvăm local
        if img_url:
            return download_and_save_image(img_url)

    except Exception as e:
        print(f"❌ Eroare la parsarea imaginii pentru {link}: {e}")

    return "/static/img/placeholder.png"  # Placeholder dacă nu s-a găsit o imagine validă


def can_access_image(url):
    """Verifică dacă imaginea poate fi accesată direct"""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.head(url, headers=headers, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def download_and_save_image(img_url):
    """Descarcă și salvează imaginea local pentru a evita restricțiile CORS"""
    import os
    from urllib.parse import urlparse
    import requests

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(img_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Eroare la descărcare: {img_url} - Status {response.status_code}")
            return "/static/img/placeholder.png"

        # 🔹 Creăm un nume de fișier unic pe baza URL-ului imaginii
        parsed_url = urlparse(img_url)
        img_name = os.path.basename(parsed_url.path)
        img_dir = os.path.join(os.getcwd(), "static", "images")  # Asigură că folderul este corect
        img_path = os.path.join(img_dir, img_name)

        # 🔹 Verificăm dacă folderul `static/images` există, altfel îl creăm
        os.makedirs(img_dir, exist_ok=True)

        # 🔹 Salvăm imaginea local
        with open(img_path, "wb") as img_file:
            img_file.write(response.content)

        # 🔹 Debugging
        print(f"✅ Imagine salvată: {img_path}")

        return f"/static/images/{img_name}"  # Returnăm calea locală a imaginii

    except Exception as e:
        print(f"❌ Eroare la descărcarea imaginii {img_url}: {e}")
        return "/static/img/placeholder.png"





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




