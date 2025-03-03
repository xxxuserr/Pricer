document.getElementById('searchButton').addEventListener('click', function(e) {
    e.preventDefault();  // Previne comportamentul implicit de trimitere al formularului

    let query = document.getElementById('search').value;
    let productList = document.getElementById('productList');
    let loader = document.getElementById('loader');

    productList.innerHTML = '';  // Curăță lista de produse
    loader.classList.remove('hidden'); // Afișează loader-ul

    // Trimite cererea AJAX pentru a căuta produsele
    fetch(`/search?query=${query}`)
        .then(response => response.json())
        .then(data => {
            loader.classList.add('hidden'); // Ascunde loader-ul

            if (data.length === 0) {
                productList.innerHTML = '<p class="no-results show">Nu au fost găsite produse.</p>';
            } else {
                data.forEach(product => {
                    let li = document.createElement('li');
                    li.innerHTML = `
                        <img src="${product.image}" alt="${product.name}">
                        <div>
                            <strong><a href="${product.link}" target="_blank">${product.name}</a></strong><br>
                            <span class="price">${product.price} lei</span>
                        </div>
                    `;
                    productList.appendChild(li);
                });
            }
        })
        .catch(error => {
            loader.classList.add('hidden'); // Ascunde loader-ul în caz de eroare
            productList.innerHTML = '<p class="no-results show">A apărut o eroare la căutare.</p>';
            console.error('Error:', error);
        });
});

// Dark Mode Toggle
document.getElementById('darkModeToggle').addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
});

// Funcție pentru a adăuga la favorite
function addToFavorites(product) {
    fetch('/add_favorite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(product)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);  // Notificare utilizator
    })
    .catch(error => console.error('Eroare la adăugarea în favorite:', error));
}

// Funcție pentru a încărca favoritele
function loadFavorites() {
    fetch('/get_favorites')
        .then(response => response.json())
        .then(data => {
            let favoriteList = document.getElementById('favoriteList');
            favoriteList.innerHTML = '';  // Curăță lista înainte de afișare

            if (data.length === 0) {
                favoriteList.innerHTML = '<p>Nu ai produse favorite.</p>';
            } else {
                data.forEach(product => {
                    let li = document.createElement('li');
                    li.innerHTML = `
                        <img src="${product.image}" alt="${product.name}">
                        <div>
                            <strong><a href="${product.link}" target="_blank">${product.name}</a></strong><br>
                            <span class="price">${product.price} MDL</span>
                            <button class="remove-favorite" onclick="removeFromFavorites('${product.name}')">❌ Elimină</button>
                        </div>
                    `;
                    favoriteList.appendChild(li);
                });
            }
        })
        .catch(error => console.error('Eroare la încărcarea favoritelor:', error));
}

// Funcție pentru eliminarea din favorite
function removeFromFavorites(name) {
    fetch('/remove_favorite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        loadFavorites();  // Reîncarcă lista de favorite
    })
    .catch(error => console.error('Eroare la eliminarea din favorite:', error));
}
