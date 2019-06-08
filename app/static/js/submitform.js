function make_request() { 
    let queryField = document.getElementById('queryField').value;
    let limitField = document.getElementById('limitField').value;
    const http = new XMLHttpRequest();
    const queryUrl = encodeURIComponent(`${queryField}`)
    const limitUrl = encodeURIComponent(`${limitField}`)
    url = `${window.location.origin}/api/player?query=${queryUrl}&limit=${limitUrl}`
    http.open('GET', url);
    http.send();
    http.onreadystatechange = () => {
        if (http.readyState == 4) {
            let parsedResponse = JSON.stringify(JSON.parse(http.responseText), undefined, 2);
            document.getElementById('playerResponse').innerHTML = parsedResponse;
        }
    }
}