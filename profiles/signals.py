# profiles/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Member

@receiver(post_save, sender=User)
def create_member_profile(sender, instance, created, **kwargs):
    if created:
        Member.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_member_profile(sender, instance, **kwargs):
    if hasattr(instance, 'member'):
        instance.member.save()

@receiver(pre_save, sender=Member)
def delete_old_profile_picture(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Member.objects.get(pk=instance.pk).profile_picture
    except Member.DoesNotExist:
        return
    new = instance.profile_picture
    if old and old.name and old.name != getattr(new, "name", None):
        old.storage.delete(old.name)