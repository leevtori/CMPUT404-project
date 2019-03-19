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
