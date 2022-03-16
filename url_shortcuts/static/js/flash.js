function removeFlash() {
    var flash = document.getElementById("flash");
    setTimeout(() => flash.remove(), 4000);
}

removeFlash();