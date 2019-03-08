function addFriend(friendId){
    alert("HELLLO");
    fetch("friends/add/", {
        method: 'post',
        headers: {
            'X-CSRFToken': document.cookie.split("=")[1]
        }, 
        body: JSON.stringify({'id':friendId})
    });
}


// funtion deleteFriend(friendId){
//     alert("BYEBYE");
//     fetch
// }
