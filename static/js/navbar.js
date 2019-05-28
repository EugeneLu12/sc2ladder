let navbar = document.getElementsByClassName('navBarHeader')[0];
let searchBar = document.getElementById('search')

window.addEventListener('scroll', function() {
    documentYPos = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
    //console.log(documentYPos)
    if (documentYPos > 0) {
        navbar.style.backgroundColor = 'rgb(0, 13, 30)';
        searchBar.style.backgroundColor = 'rgb(255, 255, 255, 0.05)';
    } else {
        navbar.style.backgroundColor = 'rgba(0, 0, 0, 0.75)';
        searchBar.style.backgroundColor = 'rgb(255, 255, 255, 0.05)';
    }
});