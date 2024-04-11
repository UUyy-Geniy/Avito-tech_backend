from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Banner, BannerTag


@receiver(post_save, sender=Banner)
@receiver(post_delete, sender=Banner)
def clear_cache_on_banner_change(sender, instance, **kwargs):
    # Удаляем кэш для всех тегов и фич связанных с баннером
    banner_tags = instance.banner_tags.all()
    for banner_tag in banner_tags:
        cache_key = f"banner_{banner_tag.feature_id}_{banner_tag.tag_id}"
        cache.delete(cache_key)


@receiver(post_save, sender=BannerTag)
@receiver(post_delete, sender=BannerTag)
def clear_cache_on_bannertag_change(sender, instance, **kwargs):
    # Удаляем кэш для конкретного изменения в BannerTag
    cache_key = f"banner_{instance.feature_id}_{instance.tag_id}"
    cache.delete(cache_key)
