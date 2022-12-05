accountMenuOptions = [
    "my_posts", "account_details"
]

function manageMenu(selected) {
    for (let i = 0; i < accountMenuOptions.length; i++) {
        if (accountMenuOptions[i] == selected) {
            document.getElementById(accountMenuOptions[i] + '_button').style.fontWeight = 'bold';
            document.getElementById(accountMenuOptions[i]).style.display = 'block';
            if (selected == 'my_posts') {
                MyPostsDefault();
            }
        } else {
            document.getElementById(accountMenuOptions[i] + '_button').style.fontWeight = 'normal';
            document.getElementById(accountMenuOptions[i]).style.display = 'none';
        }
    }
}

function MyPostsDefault() {
    el = document.getElementById('content-8');
    if (el != null && el.textContent.trim() === '') {
        el.innerHTML = '<p class="no_posts">No posts yet </p>';
    }
}

window.onload = (event) => {
    MyPostsDefault();
}
