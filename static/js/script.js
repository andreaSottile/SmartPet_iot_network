// Funzione per inviare una richiesta POST con i dati di un input
function sendPostRequest(url) {
    console.log("Sending POST req" + url);
    var baseUrl = "http://127.0.0.1:8000/";
    var url = baseUrl + url;
    // Creare un oggetto XMLHttpRequest per inviare la richiesta
    var xhr = new XMLHttpRequest();
    // Impostare il metodo, l'url e l'asincronia della richiesta
    xhr.open("POST", url, true);
    // Impostare un handler per gestire la risposta
    xhr.onload = function () {
        // Se la richiesta ha avuto successo, mostrare un messaggio di conferma
        if (xhr.status === 200) {
            alert("Richiesta inviata con successo");
        } else {
            // Altrimenti, mostrare un messaggio di errore
            alert("Si è verificato un errore: " + xhr.statusText);
        }
    };
    xhr.send();
}

document.addEventListener("DOMContentLoaded", function () {

    let top_food = document.getElementById("set_top_food");
    if (top_food != null) {
        console.log("added event listener to Top Food")
        top_food.addEventListener("click", function () {
            const url = "clientapp/food/set/max/";
            // Invocare la funzione sendPostRequest con l'id dell'input e l'url recuperato
            let val = parseInt(document.getElementById("threshold_top").value);
            console.log(url + node_id + "/" + val);
            if ((val) && (val > 0))
                sendPostRequest(url + node_id + "/" + val);
        });
    }

    let bottom_food = document.getElementById("set_bottom_food");
    if (bottom_food != null) {
        console.log("added event listener to bottom Food")
        bottom_food.addEventListener("click", function () {
            const url = "clientapp/food/set/min/";
            // Invocare la funzione sendPostRequest con l'id dell'input e l'url recuperato
            let val = parseInt(document.getElementById("threshold_bottom").value);
            console.log(url + node_id + "/" + val);
            if ((val) && (val > 0))
                sendPostRequest(url + "/" + node_id + "/" + val);
        });
    }

    let heartbeat_low = document.getElementById("set_heartbeat_low");
    if (heartbeat_low != null) {
        console.log("added event listener to low Hb")
        hearbeat_low.addEventListener("click", function () {
            const url = "clientapp/heartbeat/set/min/";
            // Invocare la funzione sendPostRequest con l'id dell'input e l'url recuperato
            let val = parseInt(document.getElementById("heartbeat_low").value);
            console.log(url + node_id + "/" + val);
            if ((val) && (val > 0))
                sendPostRequest(url + "/" + node_id + "/" + val);
        });
    }

    let heartbeat_high = document.getElementById("set_heartbeat_high");
    if (heartbeat_high != null) {
        console.log("added event listener to high Hb")
        heartbeat_high.addEventListener("click", function () {
            const url = "clientapp/heartbeat/set/max/";
            // Invocare la funzione sendPostRequest con l'id dell'input e l'url recuperato
            let val = parseInt(document.getElementById("heartbeat_high").value);
            console.log(url + node_id + "/" + val)
            if ((val) && (val > 0))
                sendPostRequest(url + "/" + node_id + "/" + val);
        });
    }

});


