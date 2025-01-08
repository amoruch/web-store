document.getElementsByClassName('sign-up')[0].addEventListener('submit', submit);

async function submit(event) {
    event.preventDefault();
    try {
        let form = document.forms[0];
        let login = form.elements.login.value;
        let email = form.elements.email.value;
        let password1 = form.elements.password1.value;
        
        let res = await fetch("/api/sign-up", {
            method: "POST",
            body: JSON.stringify({
                login: login,
                email: email,
                password1: password1
            }),
            headers: {
                "Content-type": "application/json"
            }
        });
        let json = await res.json()
        alert(json);
    } catch {
        alert("Something went wrong");
    }
}