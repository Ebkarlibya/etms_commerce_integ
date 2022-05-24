openAppBtn = document.querySelector("#open_app");


openAppBtn.addEventListener("click", function(e) {

    var url = "intent://torous.ly/#Intent;scheme=fluxstore;package=ly.ebkar.torous;end";

    window.location.replace(url); 


})