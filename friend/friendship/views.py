from django.http import HttpResponse
from django.shortcuts import render
from friendship.models import Friend, RelationShip, Profile
from django.contrib.auth.models import User 
# Create your views here.

def add_friend(request_user, pk):
    # user = CustomUser.objects.create(username='Gamach')
    # user.set_password('1111')
    # user.save()
    # add
    # print(Profile.objects.all())
    user = Profile.objects.get(username=request_user) # admin
    # req_user = Profile.objects.get(username='Napisat') # Magomed
    # print(user)
    # req_user.send_friend_request(to_user=user)
    # user.send_friend_request(to_user=req_user)
    # user.reject_friend_request(to_user=req_user)
    # req_user.reject_friend_request(to_user=user)
    # req_user.reject_all_friend_requests()
    # print(user.show_my_friend_requests())
    # req = req_user.show_my_incoming_friend_requests()
    # user.cancel_friend_request(to_user=req_user)
    # user.cancel_all_friend_request()
    # user.accept_friend_request(to_user=req_user)
    # req_user.accept_friend_request(to_user=user)
    # user.accept_all_friend_requests()
    # user.remove_friend(to_user=req_user)
    # user.remove_all_friends()
    # req = user.show_my_friends()
    # print(user.are_friends(to_user=req_user))


def index(request):
    # add_friend(request.user, pk=1)
    # add_friend(request.user, pk=2)
    # add_friend(request.user, pk=3)
    # add_friend(request.user, pk=4)
    # add_friend(request.user, pk=5)
    # add_friend(request.user, pk=6)
    # add_friend(request.user, pk=7)
    return render(request, 'friend.html', {})

