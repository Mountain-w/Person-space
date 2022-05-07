from django.db import models
from django.contrib.auth.models import User
# Create your models here.
def upload_path(instance, filename):
    return f'{instance.user.username}/avatar/{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    nickname = models.CharField(max_length=100, null=True)
    avatar = models.FileField(upload_to=upload_path, null=True)
    introduction = models.TextField(null=True)
    brithday = models.DateTimeField(null=True)



def get_profile(self):
    if hasattr(self, '_cached_user_profile'):
        return getattr(self, '_cached_user_profile')
    if UserProfile.objects.filter(user=self).exists():
        profile = UserProfile.objects.get(user=self)
    else:
        profile = UserProfile.objects.create(
            user=self,
        )
    setattr(self, '_cached_user_profile', profile)
    return profile

User.profile = property(get_profile)