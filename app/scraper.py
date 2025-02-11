import requests

def search_product(query):
    api_key = "d11583d1fc9f9158891187ed8268a77b1d34205dbffea7fb8c018be14ecf34c4"
    search_url = f"https://serpapi.com/search.json?q={query}&api_key={api_key}"

    response = requests.get(search_url)
    
    
    #print(response.json())

    results = response.json()

    products = []
    for result in results.get('shopping_results', []):
        name = result.get('title', 'No title')
        price = result.get('price', 'Price not available')
        if price != 'Price not available':
            price = price.split()[0]
        rating = result.get('rating', 'No rating')

        products.append({
            'name': name,
            'price': price,
            'rating': rating
        })
    
    return products
