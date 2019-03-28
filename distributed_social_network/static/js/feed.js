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

    //highlight selected post type
    //gives illusion of tabs
    // var all_post_btns = document.getElementsByClassName("post_btn");
    // all_post_btns[0].style.backgroundColor = '#3D9970';
    // all_post_btns[1].style.backgroundColor = '#3D9970';
    // all_post_btns[2].style.backgroundColor = '#3D9970';
    // all_post_btns[3].style.backgroundColor = '#3D9970';
    // if(post_type == 'textPost'){
    //     all_post_btns[0].style.backgroundColor = '#78cfa8';
    // }
    // else if(post_type == 'markdownPost'){
    //     all_post_btns[1].style.backgroundColor = '#78cfa8';
    // }
    // else if(post_type == 'picturePost'){
    //     all_post_btns[2].style.backgroundColor = '#78cfa8';
    // }
    // else if(post_type == 'urlPicturePost'){
    //     all_post_btns[3].style.backgroundColor = '#78cfa8';
    // }


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





























function createTextPost(){
        var id = uuidv4();
        var data = {
            "id":id,
            "type":document.getElementById("plaintype").value,
            "title":document.getElementById("plaintitle").value,
            "description":document.getElementById("plaindescription").value,
            "content":document.getElementById("plaincontent").value,
            "visibility":document.getElementById("plainvisibility").value
        };
        var csrftoken = getCookie('csrftoken');

        fetch("/posts/"+id,{
	        method: "POST",
            headers:{
	            "X-CSRFToken":csrftoken,
	            "Content-type":"application/json"
            },
            body:JSON.stringify(data)
        },).then((response)=>{
            if (response.status==200){
                alert('Your post has been created, the page will refresh now');
                location.reload();
            }
            else{
                alert('something went wrong, please try again');
            }

        });

  }
  function createMarkdownPost(){
        var id = uuidv4();
        var csrftoken = getCookie('csrftoken');
        var data = {
            "id":id,
            "type":document.getElementById("mdtype").value,
            "title":document.getElementById("mdtitle").value,
            "description":document.getElementById("mddescription").value,
            "content":document.getElementById("mdcontent").value,
            "visibility":document.getElementById("mdvisibility").value
        };

        fetch("/posts/"+id,{
	        method: "POST",
            headers:{"Content-type":"application/json","X-CSRFToken":csrftoken},
            body:JSON.stringify(data)
        }).then((response)=>{
            if (response.status==200){
                alert('Your post has been created, the page will refresh now');
                location.reload();
            }
            else{
                alert('something went wrong, please try again');
            }

        });

  }
  function createPicturePost(){
        var id = uuidv4();
        var csrftoken = getCookie('csrftoken');
        var data = {
            "id":id,
            "type":document.getElementById("picture_type").value,
            "title":document.getElementById("imgtitle").value,
            "description":document.getElementById("imgdescription").value,
            "content":document.getElementById("hiddencontent").value,
            "visibility":document.getElementById("imgvisibility").value
        };
        fetch("/posts/"+id,{
	        method: "POST",
            headers:{"Content-type":"application/json","X-CSRFToken":csrftoken,},
            body:JSON.stringify(data)
        }).then((response)=>{
            if (response.status==200){
                alert('Your post has been created, the page will refresh now');
                location.reload();
            }
            else{
                alert('something went wrong, please try again');
            }

        });

  }