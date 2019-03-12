function addFriend(friendId){
    fetch("friends/add/", {
        method: 'post',
        headers: {
            'X-CSRFToken': document.cookie.split("=")[1]
        }, 
        body: JSON.stringify({'id':friendId})
    });
};


function deleteFriend(friendId){
    fetch("friends/delete/", {
        method: 'delete', 
        headers: {
            'X-CSRFToken': document.cookie.split("=")[1]
        },
        body: JSON.stringify({'id':friendId})
    });
    alert("sucess!")
}

function confirmFriend(friendId){
    fetch("followers/confirm", {
        method: 'post',
        headers: {
            'X-CSRFToken': document.cookie.split("=")[1]
        }, 
        body: JSON.stringify({'id':friendId})
    });
};