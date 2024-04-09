from django.db import IntegrityError
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

from .models import Banner, BannerTag, Tag, Feature
from .serializers import BannerSerializer, FeatureSerializer, TagSerializer
from .permissions import IsAdminUser
from .exceptions import DuplicateDataException


class UserBannerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tag_id = request.query_params.get('tag_id')
        feature_id = request.query_params.get('feature_id')
        use_last_revision = self.request.query_params.get("use_last_revision") == 'true'

        if not tag_id or not feature_id:
            return Response({"error": "Некорректные данные"}, status=status.HTTP_400_BAD_REQUEST)

        banner_tags_qs = BannerTag.objects.filter(tag_id=tag_id, feature_id=feature_id)

        if not request.user.is_staff:
            banner_tags_qs = banner_tags_qs.filter(banner__is_active=True)

        try:
            banner_tag = banner_tags_qs.get()
        except BannerTag.DoesNotExist:
            return Response({"error": "Баннер не найден"}, status=status.HTTP_404_NOT_FOUND)

        if use_last_revision:
            serializer = BannerSerializer(banner_tag.banner)
            # print("Выдал из бд")
            return Response(serializer.data)
        else:
            # Получить закешированную информацию, которая была актуальна 5 минут назад
            cached_content = cache.get(f"banner_content_{banner_tag.banner.id}")
            if cached_content is None:
                serializer = BannerSerializer(banner_tag.banner)
                cached_content = serializer.data
                cache.set(f"banner_content_{banner_tag.banner.id}", cached_content, 5 * 60)
            return Response(cached_content)


class BannerView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        banners = Banner.objects.all()
        serializer = BannerSerializer(banners, many=True)
        return Response(serializer.data)

    def post(self, request):
        banner_serializer = BannerSerializer(data=request.data)
        if banner_serializer.is_valid():
            feature_id = request.data.get('feature')
            tags = request.data.get('tags', [])

            feature = get_object_or_404(Feature, pk=feature_id)

            try:
                with transaction.atomic():
                    banner = banner_serializer.create(request.data)

                    banner_tags = []
                    for tag_id in tags:
                        tag = get_object_or_404(Tag, pk=tag_id)
                        banner_tags.append(BannerTag(banner=banner, tag=tag, feature=feature))

                    BannerTag.objects.bulk_create(banner_tags)
            except IntegrityError:
                raise DuplicateDataException()

            return Response(banner_serializer.data, status=status.HTTP_201_CREATED)
        return Response(banner_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BannerUpdateDestroyView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(Banner, pk=pk)

    def patch(self, request, pk):
        banner = self.get_object(pk)
        serializer = BannerSerializer(banner, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        banner = self.get_object(pk)
        banner.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FeatureCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = FeatureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
