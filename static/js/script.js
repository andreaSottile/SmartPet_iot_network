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
    // Aggiungere un listener per il click sul div con classe "button" dentro il div con id "set_top_food"
    document.querySelector("#set_top_food .button").addEventListener("click", function () {
        // Recuperare l'url dal data attribute del div
        var url = this.getAttribute("data-url");
        // Invocare la funzione sendPostRequest con l'id dell'input e l'url recuperato
        sendPostRequest("threshold_top", url);
    });

    // Aggiungere un listener per il click sul div con classe "button" dentro il div con id "set_bottom_food"
    document.querySelector("#set_bottom_food .button").addEventListener("click", function () {
        // Recuperare l'url dal data attribute del div
        var url = this.getAttribute("data-url");
        // Invocare la funzione sendPostRequest con l'id dell'input e l'url recuperato
        sendPostRequest("threshold_bottom", url);
    });

    // Aggiungere un listener per il click sul div con classe "button" dentro il div con id "set_heartbeat_low"
    document.querySelector("#set_heartbeat_low .button").addEventListener("click", function () {
        // Recuperare l'url dal data attribute del div
        var url = this.getAttribute("data-url");
        // Invocare la funzione sendPostRequest con l'id dell'input e l'url recuperato
        sendPostRequest("heartbeat_low", url);
    });

    // Aggiungere un listener per il click sul div con classe "button" dentro il div con id "set_heartbeat_high"
    document.querySelector("#set_heartbeat_high .button").addEventListener("click", function () {
        // Recuperare l'url dal data attribute del div
        var url = this.getAttribute("data-url");
        // Invocare la funzione sendPostRequest con l'id dell'input e l'url recuperato
        sendPostRequest("heartbeat_high", url);
    });

});


