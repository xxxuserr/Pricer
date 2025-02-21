document.getElementById('searchButton').addEventListener('click', function() {
    let query = document.getElementById('search').value;
    let productList = document.getElementById('productList');
    let loader = document.getElementById('loader');

    productList.innerHTML = '';
    loader.classList.remove('hidden'); // Afișează loader-ul

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
        });
});

// Dark Mode Toggle
document.getElementById('darkModeToggle').addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
});
