function hideCustomId() {
    var checkBox = document.getElementById("custom_on");
    var input = document.getElementById("custom");

    if (checkBox.checked == true) {
        input.style.display = "block";
    } else {
        input.style.display = "none";
    }
}

function removeFlash() {
    var flash = document.getElementById("flash");
    setTimeout(() => flash.remove(), 3000);
}

hideCustomId();
removeFlash();