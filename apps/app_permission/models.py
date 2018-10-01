from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

from app_permission import settings

# ↓static ##############################################################################################################
class UserProfile(AbstractUser):
    user_id = models.OneToOneField(
        to=settings.USER_RESOURCE_MODEL,
        to_field=settings.USER_ID_RESOURCE_FIELD,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )


class MainMenuItem(models.Model):
    item = models.OneToOneField(Permission, on_delete=models.CASCADE)
    parent_perm = models.ForeignKey(Permission, blank=True, null=True, on_delete=models.CASCADE, related_name='parent_item')
    display_order = models.SmallIntegerField(null=True, blank=True)      # 在菜单栏的先后顺序，根条目必填

    class Meta:
        verbose_name = '菜单及功能'
        verbose_name_plural = verbose_name

    def __str__(self):
        caption_list = [self.item.name, ]
        p = self.parent_perm
        while p:
            caption_list.insert(0, p.name)
            p = getattr(p, 'parent_perm', None)
        return '-'.join(caption_list)
# ↑static ##############################################################################################################


