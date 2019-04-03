function addFriend(friendId){
    fetch(window.location.origin+"/users/friends/add/", {
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








