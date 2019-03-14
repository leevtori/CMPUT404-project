function getimageformat() {
    var  selected_picture  = document.getElementById('createPostButton').files[0];
    var invis_field;
    if (selected_picture.type == 'image/jpeg') {
            invis_field = document.getElementById("picture_type");
            invis_field.value = 'image/jpeg';
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