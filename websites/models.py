from django.db import models
from django.conf import settings

class Website(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.JSONField()  # Store structure, layout, images, etc.
    created_at = models.DateTimeField(auto_now_add=True)
