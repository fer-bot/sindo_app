from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.db.models import OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce
from django.http import Http404

from maindashboard.views.main.user_permissions import permissions
from maindashboard.models import DeliveryParty, Marking, OrderItem, TransferInfo, TransferLogisticDetail


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.WAREHOUSE_ITEMS).first() != None, login_url='/login')
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


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.WAREHOUSE_ITEMS).first() != None, login_url='/login')
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
        try:
            quantity_unit = request.POST["quantityUnit"]
            delivery_party = DeliveryParty.objects.get(
                pk=request.POST["deliveryParty"])
            marking = Marking.objects.get(pk=request.POST["marking"])
            product_name = request.POST["productName"]
            product_img = request.FILES.get("productImage", None)
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


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.WAREHOUSE_ITEMS).first() != None, login_url='/login')
def warehouse_items_edit(request, item_id):
    if request.method == 'GET':
        item = get_object_or_404(OrderItem, pk=item_id)
        item.entry_date = item.entry_date.strftime("%Y-%m-%d")

        deliveryParty = DeliveryParty.objects.order_by('name')
        markings = Marking.objects.order_by('name')

        location = request.GET.get('location', '')
        if location not in ('shenzhen warehouse', 'guangzhou warehouse'):
            Http404("Invalid location")
        transfer_to = TransferInfo.objects.filter(
            order_item=item).filter(to_detail=location).aggregate(total_box=Sum('order_quantity'))
        transfer_from = TransferInfo.objects.filter(
            order_item=item).filter(from_detail=location).aggregate(total_box=Sum('order_quantity'))

        context = {
            'item': item,
            'qtyTransferInfo': transfer_to["total_box"] - transfer_from["total_box"],
            'deliveryParty': deliveryParty,
            'markings': markings,
            'selectedDeliveryParty': item.delivery_party,
            'selectedMarking': item.marking,
            'location': location
        }
        template = loader.get_template(
            'warehouse/warehouse_items/warehouse_items_edit.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        location = request.GET.get('location', '')
        if location not in ('shenzhen warehouse', 'guangzhou warehouse'):
            Http404("Invalid location")
        try:
            quantity_unit = request.POST["quantityUnit"]
            product_name = request.POST["productName"]
            product_img = request.FILES.get("productImage", False)
            entry_date = request.POST["entryDate"]
            volume = request.POST["volume"]
            weight = request.POST["weight"]
            description = request.POST["description"]
            order_quantity = request.POST["quantity"]

            prev_qty = request.POST["prevQuantity"]

            item = get_object_or_404(OrderItem, pk=item_id)
            item.quantity_unit = quantity_unit
            item.product_name = product_name
            item.entry_date = entry_date
            item.volume = volume
            item.weight = weight
            item.description = description
            if product_img:
                item.product_img = product_img
            item.save()

            qty_changes = int(order_quantity)-int(prev_qty)

            if qty_changes != 0:
                newTransferInfo = TransferInfo(
                    from_detail='china retail',
                    to_detail=location,
                    order_item=item,
                    order_quantity=qty_changes,
                    volume=item.volume,
                    weight=item.weight,
                    description="automated"
                )
                newTransferInfo.save()

            messages.info(
                request, f'Successfully changing the details')
            return redirect('/warehouse/items')
        except:
            messages.info(
                request, f'Failed! Please re-check the starred input and try again!')
            return redirect(f'/warehouse/items/edit/{item_id}?location={location}')


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.WAREHOUSE_ITEMS).first() != None, login_url='/login')
def warehouse_items_move(request, item_id):
    if request.method == 'GET':
        try:
            order = get_object_or_404(OrderItem, pk=item_id)
            transfer_to_sz = TransferInfo.objects.filter(
                order_item=item_id).filter(to_detail="shenzhen warehouse").aggregate(total_box=Coalesce(Sum('order_quantity'), 0))
            transfer_from_sz = TransferInfo.objects.filter(
                order_item=item_id).filter(from_detail="shenzhen warehouse").values("order_item").aggregate(total_box=Coalesce(Sum('order_quantity'), 0))

            transfer = TransferInfo(
                from_detail='shenzhen warehouse',
                to_detail='guangzhou warehouse',
                order_item=order,
                order_quantity=transfer_to_sz['total_box'] -
                transfer_from_sz['total_box'],
                volume=order.volume,
                weight=order.weight,
                description="automated, moved from shenzhen warehouse to guangzhou warehouse",
            )
            transfer.save()
            messages.info(
                request, f'Moving item {item_id} from shenzhen to guangzhou successful!')
            return redirect('/warehouse/items')
        except:
            messages.info(
                request, f'Moving item {item_id} from shenzhen to guangzhou unsuccessful! Please try again.')
            return redirect('/warehouse/items')
