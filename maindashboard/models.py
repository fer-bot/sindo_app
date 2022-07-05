from statistics import mode
from django.db import models
from django.contrib.auth.models import User


class DeliveryParty(models.Model):
    name = models.CharField(unique=True, max_length=200)

    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)


class Marking(models.Model):
    name = models.CharField(unique=True, max_length=200)

    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)


class OrderItem(models.Model):
    warehousing_number = models.BigAutoField(primary_key=True)
    quantity_unit = models.CharField(max_length=20, default="box")
    delivery_party = models.ForeignKey(
        DeliveryParty, on_delete=models.CASCADE, null=False, blank=False)
    marking = models.ForeignKey(
        Marking, on_delete=models.CASCADE, null=False, blank=False)
    product_name = models.CharField(max_length=300, null=False, blank=False)
    product_img = models.ImageField(null=True, blank=True)
    entry_date = models.DateField()
    volume = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)


class TransferLogisticDetail(models.Model):
    cabinet_time = models.DateTimeField(null=False, blank=False)
    loading_location = models.CharField(
        max_length=100, null=False, blank=False)
    booking_number = models.BigIntegerField(null=False, blank=False)
    cabinet_number = models.CharField(max_length=100, null=False, blank=False)
    title = models.CharField(max_length=100, null=False, blank=False)
    cabinet_weight = models.IntegerField(null=False, blank=False)
    cabinet_type = models.CharField(max_length=50, null=False, blank=False)
    license_plate = models.CharField(max_length=50, null=False, blank=False)
    driver_name = models.CharField(max_length=100, null=True, blank=True)
    driver_phone = models.CharField(max_length=20, null=False, blank=False)
    arrived_at = models.DateTimeField(null=True, blank=True)

    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)


class TransferInfo(models.Model):
    from_detail = models.CharField(
        max_length=200, null=False, blank=False, db_index=True)
    to_detail = models.CharField(
        max_length=200, null=False, blank=False, db_index=True)
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, null=False, blank=False, db_index=True)
    order_quantity = models.IntegerField(null=False, blank=False)
    volume = models.FloatField(null=False, blank=False)
    weight = models.FloatField(null=False, blank=False)
    transfer_logistic_detail = models.ForeignKey(
        TransferLogisticDetail, on_delete=models.CASCADE, null=True, blank=True, db_index=True)

    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)


class TransferMoneyDetail(models.Model):
    transfer_info = models.OneToOneField(
        TransferInfo, on_delete=models.CASCADE, null=False, blank=False, primary_key=True)
    price = models.BigIntegerField(null=False, blank=False)
    turnover = models.BigIntegerField(null=False, blank=False)

    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)
