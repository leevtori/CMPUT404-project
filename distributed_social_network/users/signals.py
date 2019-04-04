from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Node

@receiver(post_save, sender=Node)
def nodeSaveHandler(sender, **kwargs):
    """
    Set user.is_active  to match node.active
    """
    #  get the instance
    node = kwargs.get("instance")
    user = node.user_auth
    user.is_active = node.active
    user.save()
