from django.db import models
from users.models import User

# Create your models here.
class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=100, default="")
    def __str__(self):
        return self.name

class RidePost(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    departure_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='departure_city')
    destination_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='destination_city')
    details = models.TextField()
    departure_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    available_seats = models.PositiveIntegerField(default=0) 

    def __str__(self):
        return f"{self.driver.name} -> {self.destination_city.name}"
    
class TripHistory(models.Model):
    post = models.ForeignKey(RidePost, on_delete=models.CASCADE, db_column='post_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    role = models.CharField(max_length=50)  
    trip_date = models.DateTimeField()
    status = models.CharField(max_length=50)
    is_approved = models.BooleanField(default=False)  

    class Meta:
        db_table = 'trip_history'
        managed = False  

    def __str__(self):
        return f"{self.user.name} - {self.role} - {self.status} - Approved: {self.is_approved}"