document.getElementById('search-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Previne reîncărcarea paginii

    const query = document.getElementById('search-query').value;

    if (query.trim() === '') {
        alert('Te rugăm să introduci un termen de căutare.');
        return;
    }

    fetch(`http://127.0.0.1:5000/search?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById('results');
            resultsContainer.innerHTML = ''; // Curăță rezultatele anterioare

            if (data.inline_products && data.inline_products.length > 0) {
                data.inline_products.forEach(product => {
                    const productElement = document.createElement('div');
                    productElement.classList.add('product');
                    productElement.innerHTML = `
                        <h3>${product.title}</h3>
                        <p>Preț: ${product.price} ${product.currency}</p>
                        <img src="${product.thumbnail}" alt="${product.title}" style="width: 150px;">
                    `;
                    resultsContainer.appendChild(productElement);
                });
            } else {
                resultsContainer.innerHTML = '<p>No results found.</p>';
            }
        })
        .catch(error => {
            console.error('Eroare la preluarea datelor:', error);
            alert('A apărut o eroare la căutare.');
        });
});
