function make_request() { 
    let queryField = document.getElementById('queryField').value;
    let limitField = document.getElementById('limitField').value;
    //const http = new XMLHttpRequest();
    const url = `${window.location.origin}/api/player?query=${queryField}&limit=${limitField}`
    const http = new XMLHttpRequest();
    http.open('GET', url);
    http.send();
    http.onreadystatechange=(e)=> {
        console.log(http.responseText)
        parsedResponseJSON = JSON.stringify(JSON.parse(http.responseText), undefined, 2);
        document.getElementById('playerResponse').innerHTML = parsedResponseJSON;
    }
}