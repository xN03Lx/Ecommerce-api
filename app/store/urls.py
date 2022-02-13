from django.urls import path, include
from rest_framework.routers import DefaultRouter

from store.api import views

router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('orders', views.OrderViewSet)


app_name = 'store'

urlpatterns = [
    path('', include(router.urls)),
    path(
        "orders/<int:pk>/details/<int:detail_id>",
        views.OrderViewSet.as_view({
            'delete': 'delete_detail',
        }),
        name="delete_detail"),
    path(
        "products/<int:pk>/stock/",
        views.ProductViewSet.as_view({
            'put': 'set_stock',
        }),
        name="set_stock"),
]
