from django.db import models

class Choices:
    sex = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    
class User(models.Model):
    name = models.CharField(max_length=100, default="Default Name")
    email = models.EmailField(default="example@example.com", unique=True)
    phone = models.CharField(max_length=15, default="000-000-0000")
    sex = models.CharField(max_length=10, choices=Choices.sex, default="other")
    height = models.FloatField(max_length=100)
    weight = models.FloatField(max_length=100)
    city = models.CharField(max_length=50)
    avatar = models.ImageField(
        upload_to="avatars/",
        default="avatars/default-avatar.png",
        null=True,
        blank=True,
    )
    
    def __str__(self):
        return self.name + " (" + self.email + ")"