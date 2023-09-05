// Funzione per inviare una richiesta POST con i dati di un input
function sendPostRequest(inputId, url) {
    // Selezionare l'elemento input con l'id specificato
    var input = document.getElementById(inputId);
    // Creare un oggetto FormData con il valore dell'input
    var formData = new FormData();
    formData.append("value", input.value);
    // Creare un oggetto XMLHttpRequest per inviare la richiesta
    var xhr = new XMLHttpRequest();
    // Impostare il metodo, l'url e l'asincronia della richiesta
    xhr.open("POST", url, true);
    // Impostare un handler per gestire la risposta
    xhr.onload = function () {
        // Se la richiesta ha avuto successo, mostrare un messaggio di conferma
        if (xhr.status == 200) {
            alert("Richiesta inviata con successo");
        } else {
            // Altrimenti, mostrare un messaggio di errore
            alert("Si è verificato un errore: " + xhr.statusText);
        }
    };
    // Inviare la richiesta con i dati del form
    xhr.send(formData);
}

document.addEventListener("DOMContentLoaded", function () {

    let top_food = document.getElementById("set_top_food");
    if (top_food != null) {
        top_food.addEventListener("click", function () {
            // Recuperare l'url dal data attribute del div
            var url = this.getAttribute("data-url");
            // Invocare la funzione sendPostRequest con l'id dell'input e l'url recuperato

            var val = document.getElementById("threshold_top").value;
            console.log(url + "/" + val)
            sendPostRequest("threshold_top", url + "/" + val);
        });
    }

    let bottom_food = document.getElementById("set_bottom_food");
    if (bottom_food != null) {
        bottom_food.addEventListener("click", function () {
            // Recuperare l'url dal data attribute del div
            var url = this.getAttribute("data-url");
            // Invocare la funzione sendPostRequest con l'id dell'input e l'url recuperato

            var val = document.getElementById("threshold_bottom").value;
            console.log(url + "/" + val)
            sendPostRequest("threshold_bottom", url + "/" + val);
        });
    }

    let hearbeat_low = document.getElementById("set_heartbeat_low");
    if (hearbeat_low != null) {
        hearbeat_low.addEventListener("click", function () {
            // Recuperare l'url dal data attribute del div
            var url = this.getAttribute("data-url");
            // Invocare la funzione sendPostRequest con l'id dell'input e l'url recuperato
            var val = document.getElementById("heartbeat_low").value;
            console.log(url + "/" + val)
            sendPostRequest("heartbeat_low", url + "/" + val);
        });
    }

    let heartbeat_high = document.getElementById("set_heartbeat_high");
    if (heartbeat_high != null) {
        heartbeat_high.addEventListener("click", function () {
            // Recuperare l'url dal data attribute del div
            var url = this.getAttribute("data-url");
            // Invocare la funzione sendPostRequest con l'id dell'input e l'url recuperato
            var val = document.getElementById("heartbeat_high").value;
            console.log(url + "/" + val)
            sendPostRequest("heartbeat_high", url + "/" + val);
        });
    }

});


