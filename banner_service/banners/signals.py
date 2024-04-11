from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Banner, BannerTag


@receiver(post_save, sender=Banner)
def clear_cache_on_banner_save(sender, instance, **kwargs):
    """
    Очищает кэш при сохранении объекта баннера.
    """
    cache_key = f"banner_{instance.id}"
    cache.delete(cache_key)


@receiver(post_save, sender=BannerTag)
@receiver(post_delete, sender=BannerTag)
def clear_cache_on_bannertag_change(sender, instance, **kwargs):
    """
    Очищает кэш при изменении или удалении связи BannerTag.
    """
    related_banners = Banner.objects.filter(banner_tags__tag=instance.tag, banner_tags__feature=instance.feature)
    for banner in related_banners:
        cache_key = f"banner_{banner.id}"  # Ключ включает ID каждого связанного баннера
        cache.delete(cache_key)


@receiver(post_delete, sender=Banner)
def clear_cache_on_banner_delete(sender, instance, **kwargs):
    """
    Очищает кэш при удалении объекта баннера.
    """
    cache_key = f"banner_{instance.id}"  # Ключ включает ID баннера
    cache.delete(cache_key)
