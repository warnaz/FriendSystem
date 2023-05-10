from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.module_loading import import_string
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from friendship.models import Friend, RelationShip, Profile
from friendapi.serialiers import FriendshipRequestSerializer, FriendSerializer, FriendshipRequestResponseSerializer
from friendapi.services import get_profile
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.authtoken.models import Token 

User = Profile

class FriendViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Friend model
    """
    serializer_class = FriendSerializer
    queryset = Profile.objects.all()
    lookup_field = 'pk'
    
    @extend_schema(tags=['POST'], 
                   summary='Create user',
                   description='Creates a user based on tokens auth')
    def create(self, request, *args, **kwargs):
        try:
            data = {}
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            username = serializer.data.get('username', None)
            password = serializer.data.get('password')
            user = Profile.create_user(username=username, password=password)

            token = Token.objects.get(user=user)

            data['token'] = token.key
            data['username'] = serializer.data['username']
            data['password'] = serializer.data['password']
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"message": str(e)},
                status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(tags=['GET'],
                   summary='List of friends')
    def list(self, request):
        '''Friend list'''
        try:
            user = get_profile(username=request.user)
            friend_requests = user.show_my_friends()
            self.queryset = Profile.objects.all()
            self.http_method_names = ['get', 'head', 'options', ]
            return Response(FriendSerializer(friend_requests, many=True).data,)
        
        except Exception as e:
            return Response(
                {"message": str(e)},
                status.HTTP_400_BAD_REQUEST
            )
        
    @extend_schema(tags=['GET'],
                   summary='Retrive specific user')
    def retrieve(self, request, pk=None):
        user = get_profile(username=request.user)
        self.queryset = Profile.objects.all()
        requested_user = get_object_or_404(User, pk=pk)
        
        if Friend.objects.are_friends(user, requested_user):
            self.http_method_names = ['get', 'head', 'options', ]
            return Response(FriendSerializer(requested_user, many=False).data)
        else:
            return Response(
                {'message': "Friend relationship not found for user."},
                status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(tags=['GET'],
                   summary='Get incoming requests of user')
    @action(detail=False)
    def my_incoming_requests(self, request):
        user = get_profile(username=request.user)

        friend_requests = user.show_my_incoming_friend_requests()
        self.queryset = friend_requests
        return Response(
            FriendshipRequestSerializer(friend_requests, many=True).data)


    @extend_schema(tags=['GET'],
                   summary='Get outgoing requests of user')
    @action(detail=False)
    def my_outgoing_requests(self, request):
        user = get_profile(username=request.user)

        friend_requests = user.show_my_friend_requests()
        self.queryset = friend_requests
        return Response(
            FriendshipRequestSerializer(friend_requests, many=True).data)


    @extend_schema(tags=['POST'],
                   summary='Send friend request to data["to_user"]')
    @action(detail=False,
             serializer_class=FriendshipRequestSerializer,
             methods=['post'])
    def add_friend(self, request):
        """
        Add a new friend with POST data
        - to_user
        """
        try:            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = get_profile(username=request.user)
            to_user = get_profile(username=serializer.validated_data.get('to_user'))

            user.send_friend_request(to_user=to_user)
            
            return Response(
                serializer.data,
                status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status.HTTP_400_BAD_REQUEST
            )


    @extend_schema(tags=['POST'],
                    summary='Remove friend',
                   description="Remove data['to_user'] of user's friends")
    @action(detail=False, serializer_class=FriendshipRequestSerializer, methods=['post'])
    def remove_friend(self, request):
        """Deletes a friend relationship."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = get_profile(username=request.user)
            to_user = get_profile(username=serializer.validated_data.get('to_user'))
            
            user.remove_friend(to_user=to_user)
            return Response(
                {"success": f"You removed the {to_user} from your friends"},
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status.HTTP_400_BAD_REQUEST
            )


    @extend_schema(tags=['POST'],
                   summary='Accept friend request',
                   description='Expect id of profile instance')
    @action(detail=False,
             serializer_class=FriendshipRequestResponseSerializer,
             methods=['post'])
    def accept_request(self, request):
        """Accepts a friend request"""
        try:
            id = request.data.get('id', None)
            user = get_profile(username=request.user)
            friendship_request = get_profile(pk=id)
            user.accept_friend_request(to_user=friendship_request)
        
            return Response(
                {"success": f"Request accepted, user {friendship_request} added to friends."},
                status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'message': str(e)},
                status.HTTP_400_BAD_REQUEST
            )
    

    @extend_schema(tags=['POST'],
                   summary='Reject friend request',
                   description='Expect id of profile instance')
    @action(detail=False,
             serializer_class=FriendshipRequestResponseSerializer,
             methods=['post'])
    def reject_request(self, request):
        """Rejects a friend request"""
        try:
            id = request.data.get('id', None)
            user = get_profile(username=request.user)
            friendship_request = get_profile(pk=id)
            
            user.reject_friend_request(to_user=friendship_request)

            return Response(
                {"success": "Friend request denied."},
                status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'message': str(e)},
                status.HTTP_400_BAD_REQUEST
            )
    

    @extend_schema(tags=['GET'],
                   summary='Relationship status',
                   description='Relationship status between request.user and profile.pk')
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        user = get_profile(username=request.user)
        to_user = get_profile(pk=pk)
        self.queryset = Friend.objects.all()

        _status = user.are_friends(to_user=to_user)
        return Response({"status": _status})
    