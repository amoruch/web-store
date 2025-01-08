async function f() {
    try {
        let res = await fetch("/api/profile");
        let json = await res.json();
        if (res.status == 400) {
            message = json;
            alert(message);
            window.location.replace("/sign-in")
        }

        let login = json.login;
        let email = json.email;
        let password = json.password

        document.getElementsByName('login')[0].placeholder = login;
        document.getElementsByName('email')[0].placeholder = email;
        document.getElementsByName('password')[0].placeholder = password;
    } catch {
        alert("Something went wrong");
    }
}

async function delete_acc() {
    let res = await fetch("/api/delete-acc", {
        method: 'DELETE'
    });
    let json = await res.json();
    message = json;
    alert(message);
    if (res.status == 200) {
        window.location.replace("/sign-in")
    }
}

f();