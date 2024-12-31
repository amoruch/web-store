product_template = document.getElementById("product")
shop = document.getElementsByClassName("shop")[0]

let product_count = 2;

for (let i = 0; i < 5; i++) {
    let product = product_template.content.cloneNode(true);

    product.querySelector("img").src += (i % product_count + 1) + ".png";

    shop.appendChild(product);
}