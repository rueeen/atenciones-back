from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import UserProfile
from organization.models import Area


@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        default_area, _ = Area.objects.get_or_create(name='Sin área')
        UserProfile.objects.create(user=instance, area=default_area)
