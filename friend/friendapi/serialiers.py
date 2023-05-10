from rest_framework import serializers
from friendship.models import RelationShip, Profile


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'username', 'password')


class FriendshipRequestSerializer(serializers.ModelSerializer):
    to_user = serializers.CharField()
    from_user = serializers.StringRelatedField()

    class Meta:
        model = RelationShip
        fields = ('id', 'from_user', 'to_user')
        extra_kwargs = {
            'from_user': {'read_only': True},
        }


class FriendshipRequestResponseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RelationShip
        fields = ('id',)
