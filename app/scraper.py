import requests
import re

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
        print(results)
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
    try:
        response = requests.get(link)
        if response.status_code == 200:
            log_debug(f"\n Conținutul paginii {link} (primele 2000 de caractere):")
            log_debug(response.text[:1000])

            matches = re.findall(r'(\d{4,}[\.,]?\d*)\s*(MDL|lei)', response.text)
            if matches:
                for match in matches:
                    price = match[0].replace(',', '.')
                    log_debug(f" Preț găsit: {price} {match[1]}")
                    return float(price)
                log_debug(" Nu s-a găsit un preț valid.")
            else:
                log_debug(" Niciun preț MDL/lei găsit pe pagină.")
    except Exception as e:
        log_debug(f" Eroare la obținerea prețului de la link: {e}")
    
    return None
