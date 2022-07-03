from ast import Del
from itertools import product
import re
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.db.models import OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce

from maindashboard.models import DeliveryParty, Marking, OrderItem, TransferInfo, TransferLogisticDetail
from maindashboard.views.warehouse.marking import marking


def warehouse_items(request):
    if request.method == 'GET':

        transfer_to_sz = TransferInfo.objects.filter(
            order_item=OuterRef("pk")).filter(to_detail="shenzhen warehouse").values("order_item").annotate(total_box=Sum('order_quantity'))
        transfer_from_sz = TransferInfo.objects.filter(
            order_item=OuterRef("pk")).filter(from_detail="shenzhen warehouse").values("order_item").annotate(total_box=Sum('order_quantity'))
        transfer_to_gz = TransferInfo.objects.filter(
            order_item=OuterRef("pk")).filter(to_detail="guangzhou warehouse").values("order_item").annotate(total_box=Sum('order_quantity'))
        transfer_from_gz = TransferInfo.objects.filter(
            order_item=OuterRef("pk")).filter(from_detail="guangzhou warehouse").values("order_item").annotate(total_box=Sum('order_quantity'))

        orders = OrderItem.objects.all().annotate(
            sz_qty=Coalesce(Subquery(transfer_to_sz.values("total_box")), 0) -
            Coalesce(Subquery(transfer_from_sz.values("total_box")), 0)
        ).annotate(
            gz_qty=Coalesce(Subquery(transfer_to_gz.values("total_box")), 0) -
            Coalesce(Subquery(transfer_from_gz.values("total_box")), 0)
        ).exclude(sz_qty=0, gz_qty=0).order_by('entry_date')

        context = {
            'orders': orders,
        }
        template = loader.get_template(
            'warehouse/warehouse_items/warehouse_items.html')
        return HttpResponse(template.render(context, request))


def warehouse_items_new(request):
    if request.method == 'GET':
        delivery_parties = DeliveryParty.objects.order_by('name')
        markings = Marking.objects.order_by('name')
        context = {
            "delivery_parties": delivery_parties,
            "markings": markings,
        }
        template = loader.get_template(
            'warehouse/warehouse_items/warehouse_items_new.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        # print(request.FILES["productImage"], "aaa")
        # return
        try:
            quantity_unit = request.POST["quantityUnit"]
            delivery_party = DeliveryParty.objects.get(
            pk=request.POST["deliveryParty"])
            marking = Marking.objects.get(pk=request.POST["marking"])
            product_name = request.POST["productName"]
            product_img = request.FILES["productImage"]
            entry_date = request.POST["entryDate"]
            volume = request.POST["volume"]
            weight = request.POST["weight"]
            description = request.POST["description"]
            from_detail = "china retail"
            to_detail = request.POST["warehouse"]
            order_quantity = request.POST["quantity"]

            newItem = OrderItem(
                quantity_unit=quantity_unit,
                delivery_party=delivery_party,
                marking=marking,
                product_name=product_name,
                product_img=product_img,
                entry_date=entry_date,
                volume=volume,
                weight=weight,
                description=description,
            )
            newItem.save()

            newTransferInfo = TransferInfo(
                from_detail=from_detail,
                to_detail=to_detail,
                order_item=newItem,
                order_quantity=order_quantity,
                volume=volume,
                weight=weight,
                description="automated"
            )
            newTransferInfo.save()
            messages.info(
                request, f'Adding Item with ID {newItem.warehousing_number} and name {product_name} is successful!')
            return redirect('/warehouse/items')

        except:
            messages.info(
                request, f'Failed! Please re-check the starred input and try again!')
            return redirect('/warehouse/items/new')


def warehouse_items_edit(request, item_id):
    if request.method == 'GET':
        item = get_object_or_404(OrderItem, pk=item_id)
        deliveryParty = DeliveryParty.objects.order_by('name')
        item.entry_date = item.entry_date.strftime("%Y-%m-%d")
        selectedDeliveryParty = get_object_or_404(DeliveryParty, pk=item.delivery_party_id)
        selectedMarking = get_object_or_404(Marking , pk = item.marking_id)
        selectedTransferInfo = get_object_or_404(TransferInfo, pk = item.warehousing_number)
        markings =  Marking.objects.order_by('name')
        context = {
            'item': item, 
            'selectedTransferInfo' : selectedTransferInfo,
            'deliveryParty' : deliveryParty, 
            'selectedDeliveryParty' : selectedDeliveryParty,
            'selectedMarking' : selectedMarking,
            'markings' : markings
        }
        template = loader.get_template(
            'warehouse/warehouse_items/warehouse_items_edit.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        quantity_unit = request.POST["quantityUnit"]
        product_name = request.POST["productName"]
        product_img = request.FILES.get("productImage",False)
        entry_date = request.POST["entryDate"]
        volume = request.POST["volume"]
        weight = request.POST["weight"]
        description = request.POST["description"]
        order_quantity = request.POST["quantity"]

        item = get_object_or_404(OrderItem, pk=item_id)


        item.quantity_unit = quantity_unit
        item.product_name = product_name
        item.entry_date = entry_date
        item.volume = volume
        item.weight = weight
        item.description = description

        item.save()
        transferInfoSelected = TransferInfo.objects.filter(order_item_id = item_id).first()
        # print(transferInfoSelected.to_detail)
        # newTransferInfo = TransferInfo(
        #         from_detail=from_detail,
        #         to_detail=to_detail,
        #         order_item=newItem,
        #         order_quantity=order_quantity,
        #         volume=volume,
        #         weight=weight,
        #         description="automated"
        #     )
        messages.info(
                request, f'Adding Item with ID is successful!')
        return redirect('/warehouse/items')

