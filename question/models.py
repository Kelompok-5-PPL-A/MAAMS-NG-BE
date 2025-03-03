from django.db import models

class Problem(models.Model):
    user_email = models.EmailField()
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question