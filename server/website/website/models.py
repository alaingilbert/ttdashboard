from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class PasswordRecovery(models.Model):
   hash    = models.CharField(max_length=40)
   email   = models.CharField(max_length=75)
   created = models.DateField(auto_now_add=True)


class UserProfile(models.Model):
   user           = models.OneToOneField(User)
   ttuid          = models.CharField(max_length=50, null=True, blank=True)
   activation_key = models.CharField(max_length=40, null=True, blank=True)
   auth_key       = models.TextField(max_length=255, null=True, blank=True)

   def user_email(self):
      return self.user.email

def create_user_profile(sender, instance, created, **kwargs):
   if created:
      UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
