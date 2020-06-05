CMPUT404-project-socialdistribution
===================================

CMPUT404-project-socialdistribution

See project.org (plain-text/org-mode) for a description of the project.

Make a distributed social network!

Test it out for yourself!
=========================

Find the website here : https://frandzone.herokuapp.com/

Login using:
* user: chickenwang
* password: qwertypoiu

See the video demo [here](https://www.youtube.com/watch?v=2NxgAy0GY6A)

Contributors / Licensing
========================

Generally everything is LICENSE'D under the Apache 2 license by Abram Hindle.

All text is licensed under the CC-BY-SA 4.0 http://creativecommons.org/licenses/by-sa/4.0/deed.en_US

Contributors:

    Karim Baaba
    Ali Sajedi
    Kyle Richelhoff
    Chris Pavlicek
    Derek Dowling
    Olexiy Berjanskii
    Erin Torbiak
    Abram Hindle
    Braedy Kuzma

## External Code used
* [Paginator HTML](https://simpleisbetterthancomplex.com/tutorial/2016/08/03/how-to-paginate-with-django.html)

## AJAX
We used ajax to handle adding, deleting, confirming friends, as well as follow/unfollow

Add Friend
* url: /users/friends/add/
* parameter: friendid
* Successful status code 200 will update the button to "friend request sent" and an will change follow to unfollow button

Delete Friend
* url: /users/friends/delete/
* parameter: friendid
* Successful status code 200 will remove the friend from the list

Confirm Friend: 
* url: /users/requests/confirm/
* parameter: friendid
* Successful status code 200 will update the button friends and show that you are following them

Follow:
* url: users/follow/
* parameter: friendid
* Successful status code 200 will change the follow button to unfollow

Unfollow: 
* url: users/unfollow/
* parameter: friendid
* Successful status code 200 will change the unfollow button to follow
