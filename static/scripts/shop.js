product_template = document.getElementById("product")
shop = document.getElementsByClassName("shop")[0]

async function get_products(param) {
    try {
        let params = new URLSearchParams({
            order: param,
        }).toString()
        let res = await fetch("/api/products?" + params);
        let products = await res.json();

        let product_count = products.length;
        for (let i = 0; i < product_count; i++) {
            let product = document.getElementById(i + 1);
            product.querySelector("img").src = "/static/images/products/product" + (products[i][0]) + ".png";
            product.querySelector(".product-name").innerText = products[i][1];
            product.querySelector(".product-price").innerText = products[i][2];
            product.querySelector(".product-desc").innerText = products[i][3];
            //product.setAttribute("onclick", "add_in_basket(" + products[i][0] + ")");
            product.querySelector(".add-but").setAttribute("onclick", "add_in_basket(" + products[i][0] + ")");
        }
    } catch {
        alert("something went wrong");
    }
}

async function create_products() {
    try {
        let res = await fetch("/api/products?sort_by=id");
        let json = await res.json();

        let product_count = json.length;
        for (let i = 0; i < product_count; i++) {
            let product = product_template.content.cloneNode(true);
            shop.appendChild(product);
        }

        M = document.getElementsByClassName("product")
        for (let i = 0; i < product_count; i++) {
            let product = M[i];
            product.id = i + 1;
        }
    } catch {
        alert("something went wrong");
    }
}

async function change_order(param) {
    const M = ["id", "name", "name DESC"];
    for (let i = 0; i < 3; i++) {
        let button = document.getElementById("b" + i);
        if (i == param) {
            button.setAttribute("class", "active");
        } else {
            button.setAttribute("class", "");
        }
    }
    get_products(M[param])
}

async function add_in_basket(param) {
    try {
        let params = new URLSearchParams({
            product: param,
        }).toString()
        let res = await fetch("/api/add-in-basket?" + params);
        let json = await res.json();
        alert(json.res)
    } catch {
        alert("Something went wrong");
    }
}

create_products()
get_products("id")