from flask import render_template, request
from app import app

# Exemplu de produse (poți extinde ulterior)
products = [
    {'name': 'Laptop', 'stores': [
        {'name': 'Store A', 'price': 1000},
        {'name': 'Store B', 'price': 950},
        {'name': 'Store C', 'price': 1050}
    ]},
    {'name': 'Phone', 'stores': [
        {'name': 'Store A', 'price': 500},
        {'name': 'Store B', 'price': 450},
        {'name': 'Store C', 'price': 520}
    ]},
    {'name': 'Headphones', 'stores': [
        {'name': 'Store A', 'price': 80},
        {'name': 'Store B', 'price': 75},
        {'name': 'Store C', 'price': 85}
    ]}
]

@app.route('/', methods=['GET', 'POST'])
def index():
    search_results = []
    error_message = None

    if request.method == 'POST':
        search_query = request.form.get('search_query')
        
        # Căutare produs
        if search_query:
            search_results = [p for p in products if search_query.lower() in p['name'].lower()]
        else:
            error_message = "Please enter a product to search for."
    
    return render_template('index.html', products=search_results, error_message=error_message)
