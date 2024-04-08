from django.contrib import admin
from django.urls import path, include, re_path
from banners.views import (
    UserBannerView,
    BannerView,
    BannerUpdateDestroyView,
    TagCreateView, FeatureCreateView
)

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="Description of your API",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True
)


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('feature/create/', FeatureCreateView.as_view(), name='feature-create'),
    path('tag/create/', TagCreateView.as_view(), name='tag-create'),

    path('api-auth/', include('rest_framework.urls'), name='api-auth'),
    path('auth/', include('djoser.urls'), name='auth'),
    re_path('auth/', include('djoser.urls.authtoken'), name='auth-token'),

    path('user_banner/', UserBannerView.as_view(), name='user-banner'),
    path('banner/', BannerView.as_view(), name='banner-list'),
    path('banner/<int:pk>/', BannerUpdateDestroyView.as_view(), name='banner-detail'),
]
