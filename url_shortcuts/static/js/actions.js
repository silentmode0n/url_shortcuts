function hideCustomId() {
    var checkBox = document.getElementById("custom_on");
    var input = document.getElementById("custom");

    if (checkBox.checked == true) {
        input.style.display = "block";
    } else {
        input.style.display = "none";
    }
}

function hidePassword() {
    var checkBox = document.getElementById("password_on");
    var input = document.getElementById("password");

    if (checkBox.checked == true) {
        input.style.display = "block";
    } else {
        input.style.display = "none";
    }
}

function removeFlash() {
    var flash = document.getElementById("flash");
    setTimeout(() => flash.remove(), 4000);
}

hideCustomId();
hidePassword();
removeFlash();