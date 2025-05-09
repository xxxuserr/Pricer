from flask import Flask, render_template, request, send_from_directory
import requests
import os
from flask_session import Session

app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def home():
    search_query = ''
    shopping_results = []

    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            api_url = f'https://serpapi.com/search?engine=google&q={search_query}&api_key=YOUR_API_KEY'
            response = requests.get(api_url)
            data = response.json()
            shopping_results = data.get('shopping_results', [])
    
    return render_template('index.html', shopping_results=shopping_results, search_query=search_query)


# Configurăm servirea fișierelor statice
@app.route('/static/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(app.root_path, 'static/images'), filename)

if __name__ == '__main__':
    app.run(debug=True)
