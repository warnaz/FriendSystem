# Django Friend System(+Rest)
## Overview
Django Friend System allows you to do the following: 
* Register a new user; 
* Send a friend request; 
* Cancel one of your friend requests or cancel all of your requests;
* Accept/cancel friend request or accept/cancel all friend requests;
* Delete a friend or delete all your friends
* View a list of your friends;
* View a list of your outgoing/incoming friend requests;
* View the status of a relationship with a specific users
---
:white_check_mark: Django **Rest** Friend System allows you to do the following(but you can add the rest of the features if you want.):
* Register a new user; 
* Get a token
* Send a friend request; 
* Cancel one of your friend requests;
* Accept/cancel friend request;
* Delete a friend;
* View a list of your outgoing/incoming friend requests;
* View the status of a relationship with a specific users;

### :exclamation: We will work wi Django **Rest** Friend System
---
## Requirements
- Django(4.2.1)
- Python(3.10.3)
- djangorestframework
- drf-spectacular(0.26.2)
---
## Installation
First of all we need to install **dependencies** using pip 

- Install Python

`pip install python==3.10.3`

- Install Django

`pip install django==4.2.1`

- Install djangorestframework

`pip install djangorestframework`

- Install drf-spectacular(0.26.2)

`pip install drf-spectacular==0.26.2`

---
Add to your `INSTALLED_APPS`

```
INSTALLED_APPS = [
    ...
    # MyApp     
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    ...
]
```

Add settings for `REST_FRIENDSHIP` to your project `settings.py`
```
REST_FRAMEWORK = {
    # Token Auth
    'DEFAULT_AUTHENTICATION_CLASSES': [
    'rest_framework.authentication.TokenAuthentication',
    ],

    # YOUR SETTINGS
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

```

`SPECTACULAR_SETTINGS` 

```
SPECTACULAR_SETTINGS = {
    'TITLE': 'Friend Project API',
    'DESCRIPTION': 'Friend system Api',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}
```

And add our custom User model

`AUTH_USER_MODEL = 'friendship.Profile'`

---
Your urls should look like this
```
from friend import settings
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views
from friendapi.views import FriendViewSet drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = routers.DefaultRouter()
router.register('friends', FriendViewSet, 'friend')

urlpatterns = [
    # Routers
    path('', include(router.urls)),
    
    # Swagger UI:
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]
# Token
urlpatterns += [
    path('auth_token/', views.obtain_auth_token)
]
...
```
---
`signals.py` to create tokens

```
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

```

:fire: Don't forget to register signals in `app.py`

---

## Examples
---
## POST
### Create a new user 

```
curl -X POST http://127.0.0.1:8000/friends/  \ 
    -d '{
    "username": "test_user",
    "password": "string"
    }'
```
#### Response 
```
{
  "token": "aa6a76726e93fc1c039ef38a",
  "username": "test_user",
  "password": "string"
}
```

---
### Get a token
```
curl -X 'POST' 'http://localhost:8000/auth_token/' \
    -d '{
    "username": "test_user",
    "password": "string"
    }'
```

#### Response 
```
{
  "token": "aa6a76726e93fc1c039ef38a"
}
```
---

### Accept friend request. In the data you have to add a profile.id
```
curl -X 'POST' 'http://localhost:8000/friends/accept_request/' \
  -H 'Authorization: 6c9014fddaa949702744f1f7da1c391311c829f7' \
  -d '{
  "id": 2
}'
```
Response
```
{
    'to_user': 'test_user_2'
}
```
### To reject the request, do the same, but change url: `http://localhost:8000/friends/reject_request/`
---

### Send friend request
```
curl -X 'POST' 'http://localhost:8000/friends/add_friend/' \
  -H 'Authorization: e0834994e51a866d63521c45b42952ed2f81b668' \
  -d '{
  "to_user": "test_user"
}'
```

### Response
```
{
  'from_user': 'test_user_2'
  'to_user': 'test_user'
}
```

### To remove friend do the same but change url: 
`http://localhost:8000/friends/remove_friend/` 

## GET

### Get friend list

```
curl -X 'GET' 'http://localhost:8000/friends/' \
  -H 'Authorization: e0834994e51a866d63521c45b42952ed2f81b668'
```

### Response

```
{
  ["test_user", "Pavel Durov"]
}
```

### Get status of profile.id

```
curl -X 'GET' \
  'http://localhost:8000/friends/{profile.id}/status/' \
  -H 'Authorization: e0834994e51a866d63521c45b42952ed2f81b668'
```

### Response

```
{
  'status': "There is an incoming friend request"
}
```

### Get outgoing/incoming friend requests

```
curl -X 'GET' \
  'http://localhost:8000/friend/my_outgoing_requests/'
```

### Response 

```
[
  {
    'id': 1
    "from_user": "test_user", 
    "to_user": "test_user_2", 
  }
]
```
