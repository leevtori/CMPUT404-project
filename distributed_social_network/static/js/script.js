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

function openPostInterface(post_type){
    var selected_post;
    selected_post = document.getElementById(post_type);
    var all_post_divs = document.getElementsByClassName("newPost");
    // this is dumb, but for some reason the first time this is called
    // it returns nothing, so this is a band-aid fix
    if ((selected_post.style.display!="none")&&(selected_post.style.display!="block")){
        for (var i = 0; i < all_post_divs.length; i++) {
                all_post_divs[i].style.display = "none";
        }
        selected_post.style.display="block";
    }
    else {
        if (selected_post.style.display == "none") {
            for (var i = 0; i < all_post_divs.length; i++) {
                all_post_divs[i].style.display = "none";
            }
            selected_post.style.display = "block";
        } else {
            for (var i = 0; i < all_post_divs.length; i++) {
                all_post_divs[i].style.display = "none";
            }
        }
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

function show_visible_to(option, form_id) {
    if(option == 'PRIV'){
        var form = document.querySelector("#"+form_id);
        console.log(form);
        var picker=form.querySelector(".visible_to_field");
        console.log(picker);
        picker.style.display = 'block';
    }
    else{
        var form = document.querySelector("#"+form_id);
        console.log(form);
        var picker=form.querySelector(".visible_to_field");
        console.log(picker);
        picker.style.display = 'none';
    }
};

function add_visible_to_listener(){
    var form = document.getElementById('edit_post_content');
    console.log(form);
    var visib = form.querySelector("#id_visibility");
    console.log(visib);
    var sel = visib.options[visib.selectedIndex].value;
    console.log(sel);
    if(sel == 'PRIV'){
        var vis_to = form.querySelector('.visible_to_field');
        console.log(vis_to);
        vis_to.style.display = 'block';
    }
    visib.onchange = function(){
        if(sel == 'PRIV'){
            var vis_to = form.querySelector('.visible_to_field');
            console.log(vis_to);
            vis_to.style.display = 'block';
        }else{
            var vis_to = form.querySelector('.visible_to_field');
            console.log(vis_to);
            vis_to.style.display = 'none';
        }
    }
};


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





