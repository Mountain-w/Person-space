from django.db import models
from django.contrib.auth.models import User
from dynamic.models import Dynamic
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
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

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id
        ).order_by('-created_at')