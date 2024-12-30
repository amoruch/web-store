product_template = document.getElementById("product")
shop = document.getElementsByClassName("shop")[0]

for (let i = 0; i < 11; i++) {
    shop.appendChild(product_template.content.cloneNode(true));
}