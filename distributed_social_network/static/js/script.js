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
    fetch("/users/follow/", {
        method: 'post', 
        headers: {
            'X-CSRFToken': document.cookie.split("=")[1]  
        },
        body: JSON.stringify({'id':friendId})
    }).then(setTimeout(function(){window.location.reload()},500));
};

function unfollow(friendId){
    fetch("/users/unfollow/", {
        method: 'post', 
        headers: {
            'X-CSRFToken': document.cookie.split("=")[1]  
        },
        body: JSON.stringify({'id':friendId})
    }).then(setTimeout(function(){window.location.reload()},500));
};

///////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////


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

function getimageformat() {
    var reader = new FileReader();
    var select_button = document.getElementById('createPicturePostButton')
    var selected_picture  = select_button.files[0];
    invis_field = document.getElementById("image_upload");

    var hidden = document.getElementById('hiddencontent');
    reader.readAsDataURL(selected_picture);
    reader.onloadend = function(){
        hidden.value = reader.result;
    };
    if (selected_picture.type == 'image/jpeg') {
        invis_field.value = 'JPG';
    }
    else if (selected_picture.type == 'image/png'){
        invis_field.value = 'PNG'
    }
}


function openFeed(evt, feedName) {
    // Declare all variables
    var i, tabcontent, tablinks;
  
    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("feed_tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
  
    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("feed_tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
  
    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(feedName).style.display = "block";
    evt.currentTarget.className += " active";
}


function openNewPost(evt, newPostType) {
    // Declare all variables
    var i, tabcontent, tablinks;
  
    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("post_tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
  
    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("post_tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
  
    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(newPostType).style.display = "block";
    evt.currentTarget.className += " active";
}

function add_visible_to_listener(form_id){
    var form = document.getElementById(form_id);
    console.log("form=",form);
    var visib = form.querySelector("#id_visibility");
    console.log("visib=",visib);
    var sel = visib.options[visib.selectedIndex].value;
    console.log("sel=",sel);
    if(sel == 'PRIV'){
        var vis_to = form.querySelector('.visible_to_field');
        console.log("vis_to=",vis_to);
        vis_to.style.display = 'block';
    }
    visib.onchange = function(){
        var sel = visib.options[visib.selectedIndex].value;
        console.log("sel=",sel);
        if(sel == 'PRIV'){
            var vis_to = form.querySelector('.visible_to_field');
            console.log("vis_to=",vis_to);
            vis_to.style.display = 'block';
        }else{
            var vis_to = form.querySelector('.visible_to_field');
            console.log("vis_to=",vis_to);
            vis_to.style.display = 'none';
        }
    }
};

///////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////

//taken from https://stackoverflow.com/questions/105034/create-guid-uuid-in-javascript
function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}
//end of stack overflow code

//Taken from Djangon's official documentation
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}





