function getimageformat() {
    var reader = new FileReader();
    var select_button = document.getElementById('createPicturePostButton')
    var selected_picture  = select_button.files[0];
    var invis_field = document.getElementById("picture_type");

    var hidden = document.getElementById('hiddencontent');
    reader.readAsDataURL(selected_picture);
    reader.onloadend = function(){
        hidden.value = reader.result;
        alert(hidden.value);
    };
    if (selected_picture.type == 'image/jpeg') {
        invis_field.value = 'image/jpeg';
    }
    else if (selected_picture.type == 'image/png'){
        invis_field.value = 'image/png'
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
    var all_post_btns = document.getElementsByClassName("post_btn");
    all_post_btns[0].style.backgroundColor = '#3D9970';
    all_post_btns[1].style.backgroundColor = '#3D9970';
    all_post_btns[2].style.backgroundColor = '#3D9970';
    all_post_btns[3].style.backgroundColor = '#3D9970';
    if(post_type == 'textPost'){
        all_post_btns[0].style.backgroundColor = '#78cfa8';
    }
    else if(post_type == 'markdownPost'){
        all_post_btns[1].style.backgroundColor = '#78cfa8';
    }
    else if(post_type == 'picturePost'){
        all_post_btns[2].style.backgroundColor = '#78cfa8';
    }
    else if(post_type == 'urlPicturePost'){
        all_post_btns[3].style.backgroundColor = '#78cfa8';
    }


}