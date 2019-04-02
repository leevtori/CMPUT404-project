function addFriend(friendId){
    fetch("friends/add/", {
        method: 'post',
        headers: {
            'X-CSRFToken': document.cookie.split("=")[1]
        }, 
        body: JSON.stringify({'id':friendId})
    }).then(setTimeout(function(){window.location.reload()},500));
};


function deleteFriend(friendId){
    fetch("friends/delete/", {
        method: 'delete', 
        headers: {
            'X-CSRFToken': document.cookie.split("=")[1]
        },
        body: JSON.stringify({'id':friendId})
    }).then(setTimeout(function(){window.location.reload()},500));
};

function confirmFriend(friendId){
    fetch("confirm/", {
        method: 'post',
        headers: {
            'X-CSRFToken': document.cookie.split("=")[1]
        }, 
        body: JSON.stringify({'id':friendId})
    }).then(setTimeout(function(){window.location.reload()},500));
};

function follow(friendId){
    fetch("follow/", {
        method: 'post', 
        headers: {
            'X-CSRFToken': document.cookie.split("=")[1]  
        },
        body: JSON.stringify({'id':friendId})
    }).then(setTimeout(function(){window.location.reload()},500));
};

function unfollow(friendId){
    fetch("unfollow/", {
        method: 'post', 
        headers: {
            'X-CSRFToken': document.cookie.split("=")[1]  
        },
        body: JSON.stringify({'id':friendId})
    }).then(setTimeout(function(){window.location.reload()},500));
};

function show_edit_form(){
    form = document.getElementById('edit_post_content');
    form.style.display = 'block';
    post_content = document.getElementById('post_content');
    post_content.style.display = 'none';
}

function hide_edit_form(){
    form = document.getElementById('edit_post_content');
    form.style.display = 'none';
    post_content = document.getElementById('post_content');
    post_content.style.display = 'block';
}






