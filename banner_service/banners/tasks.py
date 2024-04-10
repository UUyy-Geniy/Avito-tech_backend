from celery import shared_task
from .models import Banner


@shared_task
def delete_banners_by_feature_or_tag(feature_id=None, tag_id=None):
    """Асинхронная задача удаления баннеров по ID фичи или тега."""
    if feature_id:
        banners = Banner.objects.filter(feature_id=feature_id)
    elif tag_id:
        banners = Banner.objects.filter(tags__id=tag_id)
    else:
        banners = Banner.objects.none()

    banners.delete()
