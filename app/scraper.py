import requests

def search_product(query):
    api_key = "e3959558010c1138f41f994e5cf8478a96d4634a8fbf0c477d4a59d84ecf9172"
    search_url = f"https://serpapi.com/search.json?q={query}&api_key={api_key}&hl=ro&gl=MD"

    response = requests.get(search_url)
    results = response.json()

    print(results)  # Adaugă această linie pentru a verifica ce se returnează de la API

    if not results or 'shopping_results' not in results:
        print("Nu s-au găsit produse.")
        return []

    products = []
    for result in results['shopping_results']:
        name = result.get('title', 'No title')
        price = result.get('price', 'Price not available')

        if 'now' in price.lower() or '$0.00' in price:
            continue  
        if price == 'Price not available':
            price = 'Price not available'

        link = result.get('link', '#')
        image_url = result.get('thumbnail', '#')

        products.append({
            'name': name,
            'price': price,  
            'link': link,
            'image': image_url
        })

    return products
