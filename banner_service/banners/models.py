from django.db import models


class Feature(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"Feature(name={self.name})"


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"Tag(name={self.name})"


class Banner(models.Model):
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name='banners')
    tags = models.ManyToManyField(Tag, through='BannerTag', related_name='banners')
    content = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BannerTag(models.Model):
    banner = models.ForeignKey(Banner, related_name='banner_tags', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tag', 'feature')
