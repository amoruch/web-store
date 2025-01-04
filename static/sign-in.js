document.getElementsByClassName('sign-in')[0].addEventListener('submit', submit);

async function submit(event) {
    event.preventDefault();
    let name = "sinny";
    let email = "demon@suc.hell";
    let password = "dick";
    let res = await fetch("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({
            name: name,
            email: email,
            password: password
        }),
        headers: {
            "Content-type": "application/json"
        }
    });
    alert(res.status);
}