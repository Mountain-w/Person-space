from django.db import models
from django.contrib.auth.models import User
from dynamic.models import Dynamic
# Create your models here.


class NewsFeed(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    dynamic = models.ForeignKey(
        Dynamic,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        unique_together = (('user', 'dynamic'),)
        ordering = ('user', '-created_at')

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.dynamic}'