import requests

def search_product(query, min_price=None, max_price=None, sort_order='asc'):
    api_key = "e3959558010c1138f41f994e5cf8478a96d4634a8fbf0c477d4a59d84ecf9172"  # Înlocuiește cu cheia ta API
    location = "Chisinau, Moldova"
    gl = "MD"

    search_url = f"https://serpapi.com/search.json?q={query}&api_key={api_key}&location={location}&gl={gl}&hl=ro"

    response = requests.get(search_url)
    results = response.json()

    if results.get("search_metadata", {}).get("status") != "Success":
        print("Error:", results.get("search_metadata", {}).get("error"))
        return []

    products = []
    
    print("Produse găsite:")

    
    if 'shopping_results' in results:
        for result in results['shopping_results']:
            name = result.get('title', 'No title')
            link = result.get('link', '#')
            price = result.get('price', 'Price not available')
            image_url = result.get('thumbnail') or result.get('image') or result.get('og_image')
            
            
            if image_url and not validate_image_url(image_url):
                print(f"Imagine invalidă: {image_url}")
                image_url = None
            
            print(f"Produs: {name}, Imagine: {image_url}")

            products.append({
                'name': name,
                'link': link,
                'price': price,
                'image': image_url
            })
    

    if 'organic_results' in results:
        for result in results['organic_results']:
            name = result.get('title', 'No title')
            link = result.get('link', '#')
            snippet = result.get('snippet', 'No description available')
            price = None
            
            if 'lei' in snippet:
                price = snippet.split('lei')[0].strip() + ' lei'
            
            image_url = result.get('thumbnail') or result.get('image') or result.get('og_image')
            
            if image_url and not validate_image_url(image_url):
                print(f"Imagine invalidă: {image_url}")
                image_url = None
            
            print(f"Produs: {name}, Imagine: {image_url}")
            
            products.append({
                'name': name,
                'link': link,
                'snippet': snippet,
                'price': price if price else 'Price not available',
                'image': image_url
            })

    return products

def validate_image_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200 and 'image' in response.headers.get('Content-Type', '')
    except requests.RequestException:
        return False
