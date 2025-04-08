from django.db import models
from users.models import User
from rides.models import RidePost

# Create your models here.
class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer")
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewed_user")
    ride = models.ForeignKey(RidePost, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.name} -> {self.reviewed_user.name}: {self.rating}/5"