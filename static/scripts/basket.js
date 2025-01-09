item_template = document.getElementById("item")
items = document.getElementsByClassName("items")[0]

function financial(x) {
    return Number.parseFloat(x).toFixed(2);
}

function update_summary() {
    let a = document.getElementsByClassName("product-final-price");
    let total = 0;
    for (let i = 0; i < a.length; i++) {
        total += parseFloat(a[i].innerText.substring(1));
    }
    document.getElementById("subtotal").innerText = "$" + financial(total);
    document.getElementById("total").innerText = "$" + financial(total + 5.99);
}

async function get_basket() {
    try {
        let res = await fetch("/api/get-basket");
        let basket = await res.json();

        for (let i = 0; i < basket.length; i++) {
            let item = item_template.content.cloneNode(true);
            item.querySelector("img").src = "/static/images/products/product" + (basket[i].id) + ".png";
            item.querySelector(".product-name").innerText = basket[i].name;
            item.querySelector(".price").innerText = "$" + basket[i].price + " / lb";
            item.querySelector(".product-final-price").innerText = "$" + basket[i].price;

            item.querySelector("input").setAttribute("id", i + 1)
            item.querySelector("input").addEventListener("change", updateValue);
            function updateValue(event) {
                let price = parseFloat(event.target.value) * parseFloat(basket[i].price)
                document.querySelector("#product-" + event.target.id).innerText = "$" + financial(price);
                update_summary();
            }
            items.appendChild(item);
        }

        let a = document.getElementsByClassName("product-final-price");
        for (let i = 0; i < basket.length; i++) {
            a[i].setAttribute("id", "product-" + (i + 1));
        }
        update_summary()
        return;
    } catch {
        alert("something went wrong");
    }
}

get_basket()