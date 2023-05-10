from friendship.models import Profile

def get_profile(*args, **kwargs):
    return Profile.objects.get(*args, **kwargs)
