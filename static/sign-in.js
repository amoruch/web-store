document.getElementsByClassName('sign-in')[0].addEventListener('submit', submit);

async function submit(event) {
    event.preventDefault();
    try {
        let form = document.forms[0];
        let login = form.elements.login.value;
        let password = form.elements.password.value;

        let res = await fetch("/api/register", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=utf-8'
            },
            body: JSON.stringify({
                login: login,
                password: password
            })
        });

        let json = await res.json();
        let token = json.token
        alert(token);
    } catch {
        alert("Something went wrong");
    }
}