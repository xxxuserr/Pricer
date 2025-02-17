import requests

def search_product(query):
    api_key = "e3959558010c1138f41f994e5cf8478a96d4634a8fbf0c477d4a59d84ecf9172"
    search_url = f"https://serpapi.com/search.json?q={query}&api_key={api_key}"

    try:
        response = requests.get(search_url)
        response.raise_for_status()  # Verifică dacă cererea a avut succes
        results = response.json()

        if 'shopping_results' not in results:
            print("Nu au fost găsite rezultate în răspunsul API-ului.")
            return []

        products = []
        for result in results.get('shopping_results', []):
            name = result.get('title', 'No title')
            price = result.get('price', 'Price not available')
            if price != 'Price not available':
                price = price.split()[0]
            link = result.get('link', '#')
            image_url = result.get('thumbnail', '#')

            products.append({
                'name': name,
                'price': price,
                'link': link,
                'image': image_url  # Stocăm URL-ul imaginii
            })

        return products

    except requests.exceptions.RequestException as e:
        print(f"Eroare la cererea API: {e}")
        return []
