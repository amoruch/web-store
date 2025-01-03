item_template = document.getElementById("item")
items = document.getElementsByClassName("items")[0]

for (let i = 0; i < 5; i++) {
    items.appendChild(item_template.content.cloneNode(true));
}