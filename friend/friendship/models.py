from django.db import models
from django.contrib.auth.models import User
from django.db.models import QuerySet
from typing import List
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import Prefetch
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class Profile(AbstractUser):
    def __str__(self) -> str:
        return self.username

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
    
    def create_user(username, password, *args, **kwargs):
        user = Profile.objects.create(username=username)
        user.set_password(password)
        user.save()
        return user 
        
    def send_friend_request(self, to_user) -> None:
        '''Your attempt to impose friendship'''
        RelationShip.add_friend_request(from_user=self, to_user=to_user)
    
    def cancel_friend_request(self, to_user) -> None:
        '''Cancel your attempt to make friends'''
        RelationShip.reject_or_cancel(from_user=self, to_user=to_user)
    
    def cancel_all_friend_request(self) -> None:
        '''Cancel your attempt to make friends'''
        RelationShip.cancel_all(self)

    def accept_friend_request(self, to_user) -> None:
        '''Now you're in the friend zone'''
        req = RelationShip.get_relationship(from_user=to_user, to_user=self)
        Friend.objects.accept(self, to_user)
        req.delete()

    def accept_all_friend_requests(self) -> None:
        relation_obj = RelationShip.filter_relationship(to_user=self)
        if relation_obj.exists(): 
            Friend.objects.accept_all(relation_obj)
        else:
            raise Exception("You don't have any friend requests")

    def reject_friend_request(self, to_user) -> None:
        '''You don't need anyone'''
        RelationShip.reject_or_cancel(from_user=to_user, to_user=self) 
    
    def reject_all_friend_requests(self) -> None:
        RelationShip.reject_all(self)  

    def remove_friend(self, to_user) -> None:
        '''To hell with him'''
        Friend.objects.remove_friend(from_user=self, to_user=to_user) 

    def remove_all_friends(self) -> None:
        '''Why is this function needed at all?'''
        Friend.objects.remove_all_friend(user=self)  

    def show_my_friends(self) -> List['Friend']: 
        '''List of friends'''
        return Friend.objects.list_friends(user=self) 

    def show_my_friend_requests(self) -> List['RelationShip']:
        """Return a list of friendship requests from self(profile object)"""
        return RelationShip.list_receivers(self) 

    def show_my_incoming_friend_requests(self) -> List['RelationShip']:
        """Return a list of friendship requests"""
        return RelationShip.list_senders(self) 

    def are_friends(self, to_user) -> str:
        '''The status of our relationship'''
        if Friend.objects.are_friends(from_user=self, to_user=to_user):
            return f'You are friends with {to_user}'
        elif RelationShip.filter_relationship(from_user=self, to_user=to_user).exists():
            return 'There is an outgoing friend request'
        elif RelationShip.filter_relationship(from_user=to_user, to_user=self).exists():
            return 'There is an incoming friend request'
        else:
            return 'Nothing'
        

class RelationShip(models.Model):
    from_user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="friendship_requests_sent",
    )
    to_user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="friendship_requests_received",
    ) 
    
    def __str__(self):
        return f"User #{self.from_user_id} friendship requested #{self.to_user_id}"

    class Meta:
        verbose_name = ("Friendship Request")
        verbose_name_plural = ("Friendship Requests")

    def add_friend_request(from_user, to_user):
        '''Create a friendship request'''
        if from_user == to_user:
            raise Exception("You can't send a friendship request to yourself") 
        
        if Friend.objects.are_friends(from_user=from_user, to_user=to_user):
            raise Exception('You are already friends')
        
        request, created = RelationShip.objects.get_or_create(
            from_user=from_user, to_user=to_user
        )
        if not created:
            raise Exception('You have already submitted a request') 

        is_double = RelationShip.double_request(from_user, to_user)
        if is_double:
            request.delete()
    
    def double_request(from_user, to_user):
        ''' `double_request` checks whether both users have sent a friendship request to each other'''
        user_one = RelationShip.filter_relationship(from_user=to_user, to_user=from_user) 
        if user_one.exists():
            req = Profile.accept_friend_request(from_user, to_user)
            user_one.delete()
            return True 

    def cancel_all(self): 
        RelationShip.filter_relationship(from_user=self).delete() 

    def reject_or_cancel(from_user, to_user):
        '''Reject friend request or cancel own request'''
        RelationShip.get_relationship(
            from_user=from_user, to_user=to_user
        ).delete()

    def reject_all(self):
        RelationShip.filter_relationship(to_user=self).delete() 
    
    def list_senders(profile_object) -> list:
        senders = RelationShip.filter_relationship(to_user=profile_object)
        return list(senders)

    def list_receivers(profile_object) -> list:
        receivers = RelationShip.filter_relationship(from_user=profile_object)
        return list(receivers)

    def filter_relationship(*args, **kwargs) -> QuerySet: 
        requests = RelationShip.objects.prefetch_related(
            Prefetch('from_user', Profile.objects.only('username')
            )
        ).prefetch_related(
            Prefetch('to_user', Profile.objects.only('username')
            )
        ).filter(*args, **kwargs)

        return requests
    
    def get_relationship(*args, **kwargs) -> QuerySet:
        request = RelationShip.objects.get(*args, **kwargs)
        return request


class RelationManager(models.Manager): # FriendManager
    def accept(self, from_user, to_user):
        """Accept friendship request"""
        Friend.objects.create(from_user=from_user, to_user=to_user)
        Friend.objects.create(from_user=to_user, to_user=from_user)

    def accept_all(self, relation_obj):
        '''Accept all friend request'''
        for obj in relation_obj:
            Friend.objects.create(from_user=obj.from_user, to_user=obj.to_user)
            Friend.objects.create(from_user=obj.to_user, to_user=obj.from_user)
            obj.delete()

    def remove_friend(self, from_user, to_user):
        who_remove = Friend.objects.filter_friends(from_user=from_user, to_user=to_user)
        friend_del = Friend.objects.filter_friends(from_user=to_user, to_user=from_user)
        who_remove.delete()
        friend_del.delete()

    def remove_all_friend(self, user):
        self.filter_friends(from_user=user).delete()
        self.filter_friends(to_user=user).delete()

    def list_friends(self, user):
        '''List of all friends'''
        friends_q = self.filter_friends(to_user=user)
        friends = [user.from_user for user in friends_q]
        return friends
    
    def are_friends(self, from_user, to_user) -> bool:
        '''Are we friends with `to_user`?'''
        friends_q = self.filter_friends(from_user=from_user, to_user=to_user)
        if friends_q.exists():
            return True
        else:
            return False  

    def filter_friends(self, *args, **kwargs) -> QuerySet:
        requests = Friend.objects.prefetch_related(
            Prefetch('from_user', Profile.objects.only('username')
            )
        ).prefetch_related(
            Prefetch('to_user', Profile.objects.only('username')
            )
        ).filter(*args, **kwargs)

        # bool(requests) '''We can evaluate the request if you want to access by index'''

        return requests 


class Friend(models.Model):
    to_user = models.ForeignKey(Profile, models.CASCADE, related_name="friends")
    from_user = models.ForeignKey(Profile, models.CASCADE, related_name="from_relation")
    objects = RelationManager()

    def __str__(self):
        return f"{self.to_user} is a friend of {self.from_user}"

    class Meta:
        verbose_name = ("Friend")
        verbose_name_plural = ("Friends") 


