import os
from datetime import datetime

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from ampa_manager.family.models.holder.holder import Holder


@receiver(post_delete, sender=Holder)
def rename_auth_file_on_delete(sender, instance, **kwargs):
    if instance.authorization_document and os.path.isfile(instance.authorization_document.path):
        rename_file_with_prefix_and_date(instance.authorization_document.path, 'deleted')

@receiver(pre_save, sender=Holder)
def rename_auth_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Holder.objects.get(pk=instance.pk).authorization_document
        if not old_file:
            return False
    except Holder.DoesNotExist:
        return False

    new_file = instance.authorization_document
    if old_file != new_file and os.path.isfile(old_file.path):
        rename_file_with_prefix_and_date(old_file.path, 'replaced')

def rename_file_with_prefix_and_date(file_full_path, prefix):
    path_components = os.path.split(file_full_path)
    file_path = path_components[0]
    file_name = path_components[1]
    extension = file_name.split('.')[-1]
    file_name_without_extension = file_name[:-(len(extension)+1)]
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = f'{prefix}_{file_name_without_extension}_{now}.{extension}'
    new_full_path = os.path.join(file_path, new_name)
    os.rename(file_full_path, new_full_path)
