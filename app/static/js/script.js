let allProducts = [];
let currentIndex = 0; // Începem de la primul produs
const productsPerPage = 10; // Câte produse încărcăm pe pagină

// Funcția pentru afișarea produselor
function displayProducts(products) {
    let productList = document.getElementById('productList');
    productList.innerHTML = "";  // Șterge lista anterioară

    products.forEach(product => {
        console.log("🔍 Imagine produs:", product.image_url);

        let li = document.createElement('li');
        li.classList.add("product-card");

        li.innerHTML = `
            <div class="product-image-container">
                <img src="${product.image_url}" alt="${product.name}"
                    onerror="this.onerror=null; this.src='/static/img/placeholder.png'; console.log('⚠️ Imagine indisponibilă:', this.src)">

                <button class="fav-button" onclick="toggleFavorite('${product.name}')">
                    <i class="fas fa-heart"></i>
                </button>
            </div>
            <div class="product-details">
                <strong class="product-title">
                    <a href="${product.link}" target="_blank">${product.name}</a>
                </strong>
                <p class="product-specs">${product.specs || ''}</p>
                <span class="price">${product.price ? product.price + " lei" : '<span style="color: red;">Preț necunoscut</span>'}</span>
            </div>
        `;

        productList.appendChild(li);
    });

    currentIndex += productsPerPage; // Actualizăm indexul pentru următorul set de produse

    if (currentIndex >= products.length) {
        document.getElementById('loader').style.display = 'none'; // Ascunde loader-ul dacă nu mai sunt produse
    }
}

// Funcție care inițializează Lazy Loading
function setupLazyLoading() {
    let observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && currentIndex < allProducts.length) {
                displayProducts(allProducts);
            }
        });
    }, { threshold: 1.0 });

    observer.observe(document.getElementById('loader')); // Legăm loader-ul de observer
}

// Fetch pentru produse de pe server
function fetchProducts(query = "") {
    showLoader();

    fetch(`/search?query=${query}`)
        .then(response => response.json())
        .then(data => {
            console.log("📢 JSON Primit:", data);
            allProducts = data;
            currentIndex = 0;
            document.getElementById('productList').innerHTML = ""; // Ștergem produsele vechi
            displayProducts(allProducts);
            setupLazyLoading(); // Activăm Lazy Loading
        })
        .catch(error => {
            console.error('Eroare la preluarea produselor:', error);
        });
}

// Funcție pentru afișarea loader-ului
function showLoader() {
    let productList = document.getElementById('productList');
    productList.innerHTML = "";
    let loaderDiv = document.createElement("div");
    loaderDiv.className = "loader-container";
    loaderDiv.innerHTML = `<div class="spinner"></div>`;
    productList.appendChild(loaderDiv);
}

// Funcție pentru ascunderea loader-ului
function hideLoader() {
    let loader = document.querySelector(".loader-container");
    if (loader) loader.remove();
}

// Funcție pentru detectarea scroll-ului și încărcarea produselor
window.addEventListener('scroll', function() {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
        if (currentIndex < allProducts.length) {
            displayProducts(allProducts);
        }
    }
});

// Debounce pentru căutare (evităm căutarea automată nedorită)
let debounceTimer;
document.getElementById('search').addEventListener('input', function() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        console.log("Căutare inițiată");
    }, 500); // Doar debufferează input-ul, fără a căuta automat
});

// Căutare produse
document.getElementById('searchButton').addEventListener('click', function(e) {
    e.preventDefault();
    let query = document.getElementById('search').value.trim();
    let productList = document.getElementById('productList');

    if (query.length < 3) {
        alert("Introduceți cel puțin 3 caractere pentru căutare.");
        return;
    }

    showLoader(); // Afișează loader-ul înainte de a trimite cererea

    fetch(`/search?query=${query}`)
        .then(response => response.json())
        .then(data => {
            hideLoader(); // Ascunde loader-ul
            if (data.length === 0) {
                productList.innerHTML = '<p class="no-results show">Nu au fost găsite produse.</p>';
            } else {
                allProducts = data;
                currentIndex = 0;
                displayProducts(allProducts);
            }
        })
        .catch(error => {
            hideLoader(); // Ascunde loader-ul în caz de eroare
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
    let productData = {
        name: product.name,
        price: product.price,
        image: product.image,
        link: product.link
    };

    console.log("Date trimise la server:", productData); // Verifică datele trimise

    fetch('/add_favorite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
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
            favoriteList.innerHTML = '';  // Curățăm lista anterioară de favorite

            if (data.length === 0) {
                favoriteList.innerHTML = '<p>Nu ai produse favorite.</p>';
            } else {
                // Afișăm fiecare produs din favorite
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
        alert(data.message);  // Afișează mesajul din server
        loadFavorites();  // Reîncarcă lista de favorite
    })
    .catch(error => console.error('Eroare la eliminarea din favorite:', error));
}


function updateFavCount() {
    fetch('/get_favorites')
        .then(response => response.json())
        .then(data => {
            document.getElementById('favCount').innerText = data.length;
        });
}

function toggleFavorite(productName, productDetails) {
    let favButton = document.querySelector(`[onclick="toggleFavorite('${productName}')"] i`);

    // Modificăm starea butonului
    if (favButton.classList.contains("favorited")) {
        favButton.classList.remove("favorited");
        favButton.style.color = "#ccc"; // Revenire la gri
        
        // Eliminăm produsul din favorite
        fetch('/remove_favorite', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: productName })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message); // Confirmarea serverului
        })
        .catch(error => console.error('Eroare la eliminarea din favorite:', error));

    } else {
        favButton.classList.add("favorited");
        favButton.style.color = "#ff4d4d"; // Roșu când e favorit
        
        // Adăugăm produsul la favorite
        fetch('/add_favorite', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(productDetails) // Transmitem toate detaliile produsului
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message); // Confirmarea serverului
        })
        .catch(error => console.error('Eroare la adăugarea în favorite:', error));
    }
}




