let allProducts = [];
let currentIndex = 0; // Începem de la primul produs
const productsPerPage = 10; // Câte produse încărcăm pe pagină

// Funcție pentru afișarea produselor
function displayProducts(products) {
    let productList = document.getElementById('productList');
    for (let i = currentIndex; i < currentIndex + productsPerPage && i < products.length; i++) {
        let product = products[i];
        let li = document.createElement('li');
        li.innerHTML = `
            <img src="${product.image}" alt="${product.name}">
            <div>
                <strong><a href="${product.link}" target="_blank">${product.name}</a></strong><br>
                <span class="price">${product.price} lei</span>
            </div>
        `;
        productList.appendChild(li);
    }
    currentIndex += productsPerPage;
}

// Funcție pentru detectarea scroll-ului și încărcarea produselor
window.addEventListener('scroll', function() {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
        if (currentIndex < allProducts.length) {
            displayProducts(allProducts);
        }
    }
});

// Debounce pentru căutare
let debounceTimer;
document.getElementById('search').addEventListener('input', function() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        document.getElementById('searchButton').click();
    }, 500);
});

// Căutare produse
document.getElementById('searchButton').addEventListener('click', function(e) {
    e.preventDefault();
    let query = document.getElementById('search').value.trim();
    let productList = document.getElementById('productList');
    let loader = document.getElementById('loader');

    if (query.length < 3) {
        alert("Introduceți cel puțin 3 caractere pentru căutare.");
        return;
    }

    productList.innerHTML = ''; // Curățăm lista
    loader.classList.remove('hidden');

    fetch(`/search?query=${query}`)
        .then(response => response.json())
        .then(data => {
            loader.classList.add('hidden');
            if (data.length === 0) {
                productList.innerHTML = '<p class="no-results show">Nu au fost găsite produse.</p>';
            } else {
                allProducts = data;
                currentIndex = 0;
                displayProducts(allProducts);
            }
        })
        .catch(error => {
            loader.classList.add('hidden');
            productList.innerHTML = '<p class="no-results show">A apărut o eroare la căutare.</p>';
            console.error('Eroare la căutare:', error);
        });
});

// Dark Mode Toggle
document.getElementById('darkModeToggle').addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
});

// Gestionare favorite
function addToFavorites(product) {
    fetch('/add_favorite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(product)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        updateFavCount();
    })
    .catch(error => console.error('Eroare la adăugarea în favorite:', error));
}

function loadFavorites() {
    fetch('/get_favorites')
        .then(response => response.json())
        .then(data => {
            let favoriteList = document.getElementById('favoriteList');
            favoriteList.innerHTML = '';
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

function removeFromFavorites(name) {
    fetch('/remove_favorite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        loadFavorites();
    })
    .catch(error => console.error('Eroare la eliminarea din favorite:', error));
}

function updateFavCount() {
    fetch('/get_favorites')
    .then(response => response.json())
    .then(data => {
        if (data.length > 0) {
            document.querySelector('.fav-icon i').classList.add('active');
        }
    });

document.querySelector('.fav-icon i').addEventListener('click', function() {
    this.classList.toggle('active');
});
}
updateFavCount();
