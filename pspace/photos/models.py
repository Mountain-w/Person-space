from django.db import models
from django.contrib.auth.models import User
from dynamic.models import Dynamic 
from enum import Enum 
# Create your models here.
from pspace.settings import MEDIA_ROOT


def upload_path(instance, filename):
    import datetime
    import os
    cur_time = datetime.datetime.now()
    stamp = datetime.datetime.strftime(cur_time, "%Y%m%d%H%M%S")
    # return os.path.join(MEDIA_ROOT, ''.join((instance.user.username, stamp, filename)))
    return f"{instance.user.username}/{stamp}/{filename}"

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    dynamic = models.ForeignKey(Dynamic, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to=upload_path)
    has_delete = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_delete', 'created_at'),
        )
    
    def __str__(self):
        return f'{self.dynamic_id}:{self.file}'