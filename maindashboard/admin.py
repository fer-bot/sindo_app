from ast import Or
from django.contrib import admin
from .models import DeliveryParty, Marking, OrderItem, TransferLogisticDetail, TransferInfo, TransferMoneyDetail

# Register your models here.
admin.site.register(DeliveryParty)
admin.site.register(Marking)
admin.site.register(OrderItem)
admin.site.register(TransferLogisticDetail)
admin.site.register(TransferInfo)
admin.site.register(TransferMoneyDetail)
