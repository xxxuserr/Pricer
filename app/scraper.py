import requests
import re

def search_product(query, sort_option="popular"):
    api_key = "ea6b45bcc8887da0b4c0aacb646fde0eea09cc2e950cf21c3408d795abc81bfb"
    search_url = f"https://serpapi.com/search.json?q={query}&api_key={api_key}&hl=ro&gl=MD"

    try:
        # Trimitem cererea GET către API
        response = requests.get(search_url)
        
        # Verificăm dacă răspunsul are statusul 200 (succes)
        if response.status_code != 200:
            print(f"Eroare la API: {response.status_code}")
            return []  # Returnează o listă goală dacă API-ul returnează un cod de eroare

        # Parsează rezultatele în format JSON
        results = response.json()
        print(results)  # Adăugăm pentru debugging




    except requests.exceptions.RequestException as e:
        # Capturăm orice excepție care apare în timpul cererii
        print(f"Eroare la conectarea la API: {e}")
        return []  # Returnează o listă goală în caz de eroare de rețea

    products = []
    for result in results.get('shopping_results', []):
        name = result.get('title', 'No title')
        price = result.get('price', 'Price not available')

        # Extrage valoarea numerică a prețului
        price_value = None
        if price != 'Price not available':
            match = re.search(r'(\d+[\.,]?\d*)', price)
            if match:
                price_value = float(match.group(1).replace(',', '.'))

        link = result.get('link', '#')
        image_url = result.get('thumbnail', '#')
        rating = result.get('rating', 0)  # Asigură-te că ratingul este întotdeauna un număr

        # Verifică dacă datele sunt valide înainte de a le adăuga în listă
        if price_value is not None and link != '#' and image_url != '#':
            products.append({
                'name': name,
                'price': price,
                'price_value': price_value,
                'link': link,
                'image': image_url,
                'rating': rating
            })

    # Aplicăm sortarea în funcție de selecție
    if sort_option == "price_asc":
        products = sorted([p for p in products if p['price_value'] is not None], key=lambda x: x['price_value'])
    elif sort_option == "price_desc":
        products = sorted([p for p in products if p['price_value'] is not None], key=lambda x: x['price_value'], reverse=True)
    elif sort_option == "popular":
        products = sorted(products, key=lambda x: x['rating'], reverse=True)  # Sortare după rating
    elif sort_option == "recommended":
        products = sorted(products, key=lambda x: (x['rating'], x['price_value']), reverse=True)  # Recomandat = rating mare + preț bun

    return products
