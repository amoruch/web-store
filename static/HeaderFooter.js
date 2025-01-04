class MyHeader extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <a class="logo" href="/templates/home.html">World Peas</a>
            <nav class="navigation">
                <ul>
                    <li class="li-shop"><a href="/templates/shop.html">Shop</a></li>
                    <li class="li-who"><a href="/templates/home.html">Who we are</a></li>
                    <li class="li-prof"><a href="/templates/sign-in.html">My profile</a></li>
                    <li class="li-basket"><a href="/templates/basket.html">Basket (3)</a></li>
                </ul>
            </nav>
        `
    }
}

class MyFooter extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <div class="copyright">
                <a class="logo" href="/templates/home.html">World Peas</a>
                <p>Copyright © 2024 World Peas, Inc.</p>
            </div>
            <div class="contacts">
                <p>CONTACT US</p>
                <div class="contacts-imgs">
                    <img src="/static/images/contacts/Twitter.png" alt="T">
                    <img src="/static/images/contacts/Instagram.png" alt="I">
                    <img src="/static/images/contacts/YouTube.png" alt="YT">
                    <img src="/static/images/contacts/LinkedIn.png" alt="LI">
                </div>
            </div>
            <div class="subscribe">
                <p>Subscribe for freshest news</p>
                <form action="">
                    <input type="text" name="email" placeholder="you@example.com">
                    <button class="active">Subscribe</button>
                </form>
            </div>
        `
    }
}

customElements.define('my-header', MyHeader)
customElements.define('my-footer', MyFooter)