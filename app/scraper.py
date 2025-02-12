import requests

def search_product(query):
    api_key = "d11583d1fc9f9158891187ed8268a77b1d34205dbffea7fb8c018be14ecf34c4"
    search_url = f"https://serpapi.com/search.json?q={query}&api_key={api_key}"

    response = requests.get(search_url)
    results = response.json()

    #print(results)

    if not results or 'shopping_results' not in results:
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
