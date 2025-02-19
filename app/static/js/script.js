document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const sortSelect = document.getElementById('sort-option');
    let currentProducts = [];

    searchForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Previne reîncărcarea paginii

        const query = document.getElementById('search-query').value;

        if (query.trim() === '') {
            alert('Te rugăm să introduci un termen de căutare.');
            return;
        }

        fetch(`http://127.0.0.1:5000/search?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                currentProducts = data.products; // Salvează produsele inițiale
                displayProducts(currentProducts);
            })
            .catch(error => {
                console.error('Eroare la preluarea datelor:', error);
                alert('A apărut o eroare la căutare.');
            });
    });

    sortSelect.addEventListener('change', function() {
        if (currentProducts.length > 0) {
            sortProducts(sortSelect.value);
            displayProducts(currentProducts);
        }
    });

    function sortProducts(sortType) {
        console.log("Sorting by:", sortType); // Verifică ce tip de sortare este selectat
        console.log("Before sorting:", currentProducts); // Afișează produsele înainte de sortare

        if (sortType === 'price_asc') {
            currentProducts.sort((a, b) => {
                return (a.price_value || 0) - (b.price_value || 0);
            });
        } else if (sortType === 'price_desc') {
            currentProducts.sort((a, b) => {
                return (b.price_value || 0) - (a.price_value || 0);
            });
        } else if (sortType === 'popular') {
            currentProducts.sort((a, b) => b.rating - a.rating);
        } else if (sortType === 'recommended') {
            currentProducts.sort((a, b) => {
                if (b.rating === a.rating) {
                    return (a.price_value || 0) - (b.price_value || 0); // Sortare după preț dacă ratingul este același
                }
                return b.rating - a.rating; // Sortare după rating
            });
        }

        console.log("After sorting:", currentProducts); // Afișează produsele după sortare
    }

    function displayProducts(products) {
        const resultsContainer = document.getElementById('results');
        resultsContainer.innerHTML = ''; // Curăță rezultatele anterioare

        if (products.length > 0) {
            products.forEach(product => {
                const productElement = document.createElement('div');
                productElement.classList.add('product-item');
                productElement.innerHTML = `
                    <div class="product-container">
                        <img src="${product.image}" alt="${product.name}">
                        <div class="product-info">
                            <strong>
                                <a href="${product.link}" target="_blank">${product.name}</a>
                            </strong>
                            <p class="price">${product.price} lei</p>
                        </div>
                    </div>
                `;
                resultsContainer.appendChild(productElement);
            });
        } else {
            resultsContainer.innerHTML = '<p class="no-results">Nu au fost găsite produse.</p>';
        }
    }
});