from app import app

if __name__ == "__main__":
    app.run(debug=True)
if __name__ == "__main__":
    if app.config['ENV'] == 'development':
        app.run(debug=True)
    else:
        app.run(debug=False)