from django.contrib import admin
from friendship.models import Friend, Profile, RelationShip
# Register your models here.
admin.site.register(Friend)
admin.site.register(RelationShip)
admin.site.register(Profile)
