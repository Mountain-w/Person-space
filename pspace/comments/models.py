from django.db import models
from django.contrib.auth.models import User
from dynamic.models import Dynamic
# Create your models here.
class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null = True,
    )
    dynamic = models.ForeignKey(
        Dynamic,
        on_delete=models.SET_NULL,
        null=True,
    )
    content = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = (('dynamic', 'created_at'),)

    def __str__(self):
        return f"{self.created_at} - {self.user} says {self.content} at dynamic {self.dynamic_id}"