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
                            <span class="price">${product.price} RON</span>
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
