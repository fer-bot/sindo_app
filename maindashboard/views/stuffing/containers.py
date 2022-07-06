from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.db.models import OuterRef, Subquery, Sum, FloatField, ExpressionWrapper, Q, F
from django.db.models.functions import Coalesce

from maindashboard.views.main.user_permissions import permissions
from maindashboard.models import DeliveryParty, Marking, OrderItem, TransferInfo, TransferLogisticDetail, TransferMoneyDetail


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.STUFFING_CONTAINER).first() != None, login_url='/login')
def containers(request):
    if request.method == 'GET':

        containers = TransferLogisticDetail.objects.exclude(
            arrived_at__isnull=False).order_by("cabinet_time")
        context = {
            'orders': [],
            'containers': containers,
        }
        template = loader.get_template(
            'stuffing/containers/containers.html')
        return HttpResponse(template.render(context, request))


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.STUFFING_CONTAINER).first() != None, login_url='/login')
def containers_view(request, container_id):
    if request.method == 'GET':
        container = get_object_or_404(TransferLogisticDetail, pk=container_id)

        subq_money_detail = TransferMoneyDetail.objects.filter(transfer_info=OuterRef("id")).values("transfer_info").annotate(
            total_price=Sum('price'),
            total_turnover=Sum('turnover'),
        )

        items_to_container = TransferInfo.objects.filter(
            order_item=OuterRef("order_item")).filter(to_detail=f"container-{container_id}").annotate(
                price=Coalesce(
                    Subquery(subq_money_detail.values("total_price")), 0),
                turnover=Coalesce(
                    Subquery(subq_money_detail.values("total_turnover")), 0)
        ).values("order_item").annotate(
                total_box=Sum('order_quantity'),
                total_volume=Sum('volume', output_field=FloatField()),
                total_weight=Sum('weight', output_field=FloatField()),
                total_price=Sum('price'),
                total_turnover=Sum('turnover')
        )
        items_from_container = TransferInfo.objects.filter(
            order_item=OuterRef("order_item"), from_detail=f"container-{container_id}").values("order_item").annotate(
            total_box=Sum('order_quantity'),
            total_volume=Sum('volume', output_field=FloatField()),
            total_weight=Sum('weight', output_field=FloatField())
        )

        items = TransferInfo.objects.filter(
            to_detail=f"container-{container_id}").values("order_item").annotate(
                quantity=Coalesce(Subquery(items_to_container.values(
                    "total_box")), 0) - Coalesce(Subquery(items_from_container.values("total_box")), 0),
                volume=ExpressionWrapper(Coalesce(Subquery(items_to_container.values(
                    "total_volume")), 0) - Coalesce(Subquery(items_from_container.values("total_volume")), 0), output_field=FloatField()),
                weight=ExpressionWrapper(Coalesce(Subquery(items_to_container.values(
                    "total_weight")), 0) - Coalesce(Subquery(items_from_container.values("total_weight")), 0), output_field=FloatField()),
                price=Coalesce(
                    Subquery(items_to_container.values("total_price")), 0),
                turnover=Coalesce(
                    Subquery(items_to_container.values("total_turnover")), 0),
        ).distinct().order_by('order_item')

        total_box = 0
        total_vol = 0
        total_weight = 0
        total_price = 0
        total_turnover = 0

        for item in items:
            total_box += item["quantity"]
            total_vol += item["volume"]
            total_weight += item["weight"]
            total_price += item["price"]
            total_turnover += item["turnover"]

            item['item'] = OrderItem.objects.get(pk=item['order_item'])
            item['price'] = 'Rp {:,.0f}'.format(item['price'])
            item['turnover'] = 'Rp {:,.0f}'.format(item['turnover'])
            item['transfers'] = TransferInfo.objects.filter(
                Q(to_detail=f"container-{container_id}") | Q(to_detail=f"container-{container_id}"), order_item=item['order_item']).order_by('-created_at')

        context = {
            'container': container,
            'items': items,
            'total_box': total_box,
            'total_volume': total_vol,
            'total_weight': total_weight,
            'total_price': 'Rp {:,.0f}'.format(total_price),
            'total_turnover': 'Rp {:,.0f}'.format(total_turnover),
        }
        template = loader.get_template(
            'stuffing/containers/containers_view.html')
        return HttpResponse(template.render(context, request))


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.STUFFING_CONTAINER).first() != None, login_url='/login')
def containers_ship(request, container_id):
    if request.method == 'GET':
        try:
            container = get_object_or_404(
                TransferLogisticDetail, pk=container_id)
            container.shipped_at = datetime.now()
            container.save()

            messages.info(
                request, f'Shipping container id {container_id} is successful!')
            return redirect(f'/stuffing/containers')
        except:
            messages.info(
                request, f'Shipping container id {container_id} is Unsuccessful!')
            return redirect(f'/stuffing/containers')


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.STUFFING_CONTAINER).first() != None, login_url='/login')
def containers_edit_details(request, container_id):
    if request.method == 'GET':
        container = get_object_or_404(TransferLogisticDetail, pk=container_id)
        container.cabinet_time = container.cabinet_time.strftime(
            "%Y-%m-%dT%H:%M")

        context = {
            'container': container,
        }
        template = loader.get_template(
            'stuffing/containers/containers_edit_details.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        try:
            container = get_object_or_404(
                TransferLogisticDetail, pk=container_id)

            container.cabinet_time = request.POST["cabinetTime"]
            container.loading_location = request.POST["loadingLocation"]
            container.booking_number = request.POST["bookingNumber"]
            container.cabinet_number = request.POST["cabinetNumber"]
            container.title = request.POST["title"]
            container.cabinet_weight = request.POST["cabinetWeight"]
            container.cabinet_type = request.POST["cabinetType"]
            container.license_plate = request.POST["licensePlate"]
            container.driver_name = request.POST['driverName']
            container.driver_phone = request.POST['driverPhone']
            container.description = request.POST["description"]

            container.save()
            messages.info(
                request, f'Edit to container detail with ID {container_id} is successful!')
            return redirect(f'/stuffing/containers/view/{container_id}')

        except:
            messages.info(
                request, f'Edit to container detail with id {container_id} is Unsuccessful! Please try again')
            return redirect(f'/stuffing/containers/edit/{container_id}/details')


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.STUFFING_CONTAINER).first() != None, login_url='/login')
def containers_edit_item(request, container_id, item_id):
    if request.method == 'GET':
        transfer_info = TransferInfo.objects.filter(
            Q(to_detail=f"container-{container_id}") | Q(to_detail=f"container-{container_id}"), order_item=item_id)

        print(transfer_info)

        box, volume, weight, price, turnover = 0, 0, 0, 0, 0

        for transfer in transfer_info:
            if transfer.to_detail == f"container-{container_id}":
                box += transfer.order_quantity
                volume += transfer.volume
                weight += transfer.weight

                subq_money_detail = TransferMoneyDetail.objects.filter(transfer_info=transfer.id).values("transfer_info").aggregate(
                    total_price=Sum('price'),
                    total_turnover=Sum('turnover'),
                )
                price += subq_money_detail.get("total_price", 0)
                turnover += subq_money_detail.get("total_turnover", 0)

            if transfer.from_detail == f"container-{container_id}":
                box -= transfer.order_quantity
                volume -= transfer.volume
                weight -= transfer.weight

        context = {
            "container_id": container_id,
            "item_id": item_id,
            "quantity": box,
            "volume": volume,
            "weight": weight,
            "price": price,
            "turnover": turnover,
        }
        template = loader.get_template(
            'stuffing/containers/containers_edit_item.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        try:
            order = get_object_or_404(OrderItem, warehousing_number=item_id)
            container = get_object_or_404(
                TransferLogisticDetail, pk=container_id)
            weight = float(request.POST["weight"]) - \
                float(request.POST["prevWeight"])
            volume = float(request.POST["volume"]) - \
                float(request.POST["prevVolume"])
            qty = int(request.POST["quantity"]) - \
                int(request.POST["prevQuantity"])
            price = int(request.POST["price"]) - int(request.POST["prevPrice"])
            turnover = int(request.POST["turnover"]) - \
                int(request.POST["prevTurnover"])
            desc = request.POST["description"]

            transfer = TransferInfo(
                from_detail='guangzhou warehouse',
                to_detail=f"container-{container_id}",
                order_item=order,
                order_quantity=qty,
                volume=volume,
                weight=weight,
                description=desc,
                transfer_logistic_detail=container,
            )
            transfer.save()

            transfer_money_detail = TransferMoneyDetail(
                transfer_info=transfer,
                price=price,
                turnover=turnover
            )
            transfer_money_detail.save()

            messages.info(
                request, f'Edit to item detail with container id {container_id} and item id {item_id} is successful!')
            return redirect(f'/stuffing/containers/view/{container_id}')

        except:
            messages.info(
                request, f'Edit to item detail with container id {container_id} and item id {item_id} is Unsuccessful! Please try again')
            return redirect(f'/stuffing/containers/edit/{container_id}/item/{item_id}')


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.STUFFING_CONTAINER).first() != None, login_url='/login')
def containers_add_item(request, container_id):
    if request.method == 'GET':
        container = get_object_or_404(TransferLogisticDetail, pk=container_id)

        transfer_to_gz = TransferInfo.objects.filter(
            order_item=OuterRef("pk")).filter(to_detail="guangzhou warehouse").values("order_item").annotate(total_box=Sum('order_quantity'))
        transfer_from_gz = TransferInfo.objects.filter(
            order_item=OuterRef("pk")).filter(from_detail="guangzhou warehouse").values("order_item").annotate(total_box=Sum('order_quantity'))

        item_in_container = TransferInfo.objects.filter(
            to_detail=f"container-{container_id}").values("order_item").distinct()

        orders = OrderItem.objects.all().filter(verified_at__isnull=False).annotate(
            gz_qty=Coalesce(Subquery(transfer_to_gz.values("total_box")), 0) -
            Coalesce(Subquery(transfer_from_gz.values("total_box")), 0)
        ).exclude(gz_qty=0).exclude(warehousing_number__in=item_in_container).order_by('entry_date')

        context = {
            'container': container,
            'orders': orders
        }
        template = loader.get_template(
            'stuffing/containers/containers_add_item.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        try:
            container = get_object_or_404(
                TransferLogisticDetail, pk=container_id)
            order = get_object_or_404(OrderItem, pk=request.POST["orderItem"])
            weight = float(request.POST["weight"])
            volume = float(request.POST["volume"])
            qty = int(request.POST["quantity"])
            price = int(request.POST["price"])
            turnover = int(request.POST["turnover"])
            desc = request.POST["description"]

            transfer = TransferInfo(
                from_detail='guangzhou warehouse',
                to_detail=f"container-{container_id}",
                order_item=order,
                order_quantity=qty,
                volume=volume,
                weight=weight,
                description=desc,
                transfer_logistic_detail=container,
            )
            transfer.save()

            transfer_money_detail = TransferMoneyDetail(
                transfer_info=transfer,
                price=price,
                turnover=turnover
            )
            transfer_money_detail.save()

            messages.info(
                request, f'Adding item detail is Successful! Please try again')
            return redirect(f'/stuffing/containers/view/{container_id}')
        except:
            messages.info(
                request, f'Adding item detail is Unsuccessful! Please try again')
            return redirect(f'/stuffing/containers/edit/{container_id}/add_item')


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.STUFFING_CONTAINER).first() != None, login_url='/login')
def containers_new(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template(
            'stuffing/containers/containers_new.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        try:
            container = TransferLogisticDetail(
                cabinet_time=request.POST["cabinetTime"],
                loading_location=request.POST["loadingLocation"],
                booking_number=request.POST["bookingNumber"],
                cabinet_number=request.POST["cabinetNumber"],
                title=request.POST["title"],
                cabinet_weight=request.POST["cabinetWeight"],
                cabinet_type=request.POST["cabinetType"],
                license_plate=request.POST["licensePlate"],
                driver_name=request.POST['driverName'],
                driver_phone=request.POST['driverPhone'],
                description=request.POST["description"],
            )
            container.save()
            messages.info(
                request, f'Adding new container detail with ID {container.id} is successful!')
            return redirect(f'/stuffing/containers/view/{container.id}')

        except:
            messages.info(
                request, f'Adding new container is Unsuccessful! Please try again')
            return redirect(f'/stuffing/containers/new')
