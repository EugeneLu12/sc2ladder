let input = document.getElementById('search');
input.addEventListener('keyup', function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        console.log(input.value);
        search_str = input.value;
        if (search_str.indexOf('#') !== -1) {
            search_strs = search_str.split('#')
            window.location.href = 'search?name=' + search_strs[0] + '&bnet_id=' + search_strs[1];
        } else if (search_str.indexOf('/') !== -1) {
            search_strs = search_str.split('/')
            window.location.href = 'search?profile_path=' + search_strs[4] + search_strs[5];
        } else {
            window.location.href = 'search?name=' + search_str;
        }
    }
  });