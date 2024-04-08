import json

from rest_framework import serializers
from .models import Tag, Feature, Banner, BannerTag


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class BannerTagSerializer(serializers.ModelSerializer):
    tag = serializers.SlugRelatedField(slug_field='name', queryset=Tag.objects.all())
    feature = serializers.SlugRelatedField(slug_field='name', queryset=Feature.objects.all())

    class Meta:
        model = BannerTag
        fields = ('id', 'banner', 'tag', 'feature',)


class BannerSerializer(serializers.ModelSerializer):
    banner_tags = BannerTagSerializer(many=True, read_only=True)
    feature = serializers.PrimaryKeyRelatedField(queryset=Feature.objects.all())
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Banner
        fields = '__all__'

    def create(self, validated_data):
        tags = Tag.objects.filter(pk__in=validated_data["tags"])
        banner = Banner.objects.create(feature_id=validated_data["feature"], content=validated_data["content"], is_active=validated_data["is_active"])
        return banner
