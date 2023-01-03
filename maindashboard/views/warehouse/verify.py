from datetime import datetime
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
    name=permissions.WAREHOUSE_VERIFY).first() != None, login_url='/login')
def verify(request):
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
            'warehouse/verify/verify_items.html')
        return HttpResponse(template.render(context, request))


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.WAREHOUSE_VERIFY).first() != None, login_url='/login')
def verify_item(request, item_id):
    if request.method == 'GET':
        item = get_object_or_404(OrderItem, pk=item_id)
        item.verified_at = datetime.now()
        item.save()

        messages.info(
            request, f'Verifying  Item with ID with ID {item.warehousing_number} and name {item.product_name} is successful!')
        return redirect('/warehouse/verify')


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.WAREHOUSE_VERIFY).first() != None, login_url='/login')
def verify_edit(request, item_id):
    if request.method == 'GET':
        item = get_object_or_404(OrderItem, pk=item_id)
        item.entry_date = item.entry_date.strftime("%Y-%m-%d")

        deliveryParty = DeliveryParty.objects.order_by('name')
        markings = Marking.objects.order_by('name')

        location = request.GET.get('location', '')
        if location not in ('shenzhen warehouse', 'guangzhou warehouse'):
            Http404("Invalid location")
        transfer_to = TransferInfo.objects.filter(
            order_item=item).filter(to_detail=location).aggregate(total_box=Coalesce(Sum('order_quantity'), 0))
        transfer_from = TransferInfo.objects.filter(
            order_item=item).filter(from_detail=location).aggregate(total_box=Coalasce(Sum('order_quantity'), 0))

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
            'warehouse/verify/verify_edit.html')
        return HttpResponse(template.render(context, request))

    if request.method == 'POST':
        location = request.GET.get('location', '')
        if location not in ('shenzhen warehouse', 'guangzhou warehouse'):
            Http404("Invalid location")
        try:
            quantity_unit = request.POST["quantityUnit"]
            product_name = request.POST["productName"]
            company_number = request.POST["companyNumber"]
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
            item.company_number = company_number
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
            return redirect('/warehouse/verify')
        except:
            messages.info(
                request, f'Failed! Please re-check the starred input and try again!')
            return redirect(f'/warehouse/verify/edit/{item_id}?location={location}')
