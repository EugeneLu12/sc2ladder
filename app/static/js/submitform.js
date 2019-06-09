function make_request() { 
    let queryField = document.getElementById('queryField').value;
    let limitField = document.getElementById('limitField').value;
    const queryUrl = encodeURIComponent(queryField)
    const limitUrl = encodeURIComponent(limitField)
    url = `${window.location.origin}/api/player?query=${queryUrl}&limit=${limitUrl}`
    fetch(url)
        .then(response => response.json())
        .then(data => {
            parsedResponseJSON = JSON.stringify((data), undefined, 2);
            document.getElementById('playerResponse').innerHTML = parsedResponseJSON;
        });
}