from .models import User
from django.contrib.auth.models import AnonymousUser

def notifications(request):
    user = request.user
    if(user != AnonymousUser()):
        followers= user.followers.all()
        qs = set(user.followers.all()).difference(set(user.friends.all()))
        q = len(list(qs))
        return {
            'friend_request_count': q
        }
    return {
            'friend_request_count': 0
        }