document.getElementsByClassName('sign-up')[0].addEventListener('submit', submit);

async function submit(event) {
    event.preventDefault();
    try {
        let form = document.forms[0];
        let name = form.elements.name.value;
        let email = form.elements.email.value;
        let password = form.elements.password1.value;
        
        let res = await fetch("/api/new_user", {
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
    } catch {
        alert("Something went wrong");
    }
}