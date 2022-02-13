from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.cache import cache

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from store.models import Product, Order, OrderDetail
from store.services import get_dollar_blue
from store.utils import select_for_update
from .serializers import ProductSerializer, OrderSerializer, StockSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    # permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def set_stock(self, request, pk):
        stock = request.data.get('stock')
        serializer = StockSerializer(data=request.data)
        if serializer.is_valid():
            product = select_for_update(Product, pk)
            product.set_stock(stock)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    # permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        dolar_blue = cache.get("dolar_blue")
        if dolar_blue is None:
            response = get_dollar_blue()
            if response:
                dolar_blue = response['casa']['compra']
            cache.set("dolar_blue", dolar_blue)

        return self.queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete_details()
        return super(OrderViewSet, self).destroy(request, *args, **kwargs)

    def delete_detail(self, request, pk, detail_id):
        detail = get_object_or_404(OrderDetail, pk=detail_id)
        detail.restore_stock()
        detail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
