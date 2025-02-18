// Adăugarea unui scroll to top
let mybutton = document.getElementById("scrollToTopBtn");

// Arată butonul când utilizatorul face scroll la 100px deasupra paginii
window.onscroll = function() {
    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
        mybutton.style.display = "block";
    } else {
        mybutton.style.display = "none";
    }
};

// Când se apasă pe buton, se face scroll înapoi la top
mybutton.onclick = function() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}

// Funcția de căutare a produselor
document.getElementById('searchButton').addEventListener('click', function() {
    let query = document.getElementById('search').value;
    let productList = document.getElementById('productList');

    // Găsește produsele care corespund cu căutarea (poți înlocui cu logica ta de căutare)
    let products = [
        { name: 'Produs 1', price: '100 RON' },
        { name: 'Produs 2', price: '150 RON' },
        { name: 'Produs 3', price: '200 RON' }
    ];

    // Curăță lista de produse înainte de fiecare căutare
    productList.innerHTML = '';

    // Adaugă produsele găsite
    products.forEach(product => {
        if (product.name.toLowerCase().includes(query.toLowerCase())) {
            let li = document.createElement('li');
            li.innerHTML = `
                <img src="path_to_product_image.jpg" alt="${product.name}">
                <div>
                    <h3>${product.name}</h3>
                    <p>${product.price}</p>
                </div>
            `;
            productList.appendChild(li);
        }
    });

    // Dacă nu se găsește niciun produs, afișează un mesaj
    if (productList.innerHTML === '') {
        productList.innerHTML = '<p>Nu s-au găsit produse care să corespundă căutării.</p>';
    }
});
