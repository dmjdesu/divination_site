from django.db import models
from django.contrib.auth.models import AbstractUser

class RoleChoices(models.TextChoices):
    DIBINATION = 'dibination', '占い師'
    CLIENT = 'client', '顧客'

class CustomUser(AbstractUser):
    """
    Users within the Django authentication system are represented by this
    model.

    Username and password are required. Other fields are optional.
    """

    role = models.CharField(max_length=255,choices=RoleChoices.choices,default=RoleChoices.CLIENT )

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

