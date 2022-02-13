from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework import serializers
from store.models import Product, Order, OrderDetail
from store.utils import has_values


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('id', 'name', 'stock', 'price')


class OrderDetailSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=True
    )

    class Meta:
        model = OrderDetail
        fields = ('id', 'product', 'cuantity')
        extra_kwargs = {
            'cuantity': {'required': True},
        }


class OrderSerializer(serializers.ModelSerializer):
    details = OrderDetailSerializer(
        many=True,
        required=True,
        allow_empty=False
    )
    get_total = serializers.ReadOnlyField()
    get_total_usd = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ('id', 'details', 'date_time', 'get_total', 'get_total_usd')
        read_only_fields = ('id', 'date_time')

    def validate_details(self, values):
        product_ids = []
        duplicate = set()
        for value in values:
            product_id = value['product'].id
            if product_id not in product_ids:
                product_ids.append(product_id)
            else:
                duplicate.add(str(product_id))

        if has_values(duplicate):
            string_product_ids = ", ".join(list(duplicate))
            raise serializers.ValidationError(
                f"Products with ids {string_product_ids} are repetied"
            )
        return values

    @transaction.atomic
    def create(self, validated_data):
        order = Order.objects.create()
        details = validated_data.pop('details')
        try:
            order.add_details(details)
        except ValidationError as e:
            raise serializers.ValidationError({"details": e.message})

        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        input_details = validated_data.pop('details')
        current_details = instance.details.all().select_related('product')
        details = instance.get_details_to_update_and_create(
            input_details,
            current_details
        )

        try:
            instance.add_details(details['to_add'])
            instance.update_details(details['to_update'], current_details)
        except ValidationError as e:
            raise serializers.ValidationError({"details": e.message})
        return instance


class StockSerializer(serializers.Serializer):
    stock = serializers.IntegerField(required=True, min_value=0)
