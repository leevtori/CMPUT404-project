from .models import User
from django.contrib.auth.models import AnonymousUser

def notifications(request):
    user = request.user

    if(user != AnonymousUser()):
        q = request.user.incomingRequests.all()
        count = len(q)
        return {
            'friend_request_count': count
        }
    return {
            'friend_request_count': 0
        }