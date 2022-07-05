from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.db.models import OuterRef, Subquery, Sum, FloatField, ExpressionWrapper, Q, F
from django.db.models.functions import Coalesce

from maindashboard.models import DeliveryParty, Marking, OrderItem, TransferInfo, TransferLogisticDetail, TransferMoneyDetail


def containers(request):
    if request.method == 'GET':

        containers = TransferLogisticDetail.objects.filter(
            shipped_at__isnull=True).order_by("cabinet_time")
        context = {
            'orders': [],
            'containers': containers,
        }
        template = loader.get_template(
            'stuffing/containers/containers.html')
        return HttpResponse(template.render(context, request))


def containers_view(request, container_id):
    if request.method == 'GET':
        container = get_object_or_404(TransferLogisticDetail, pk=container_id)

        subq_money_detail = TransferMoneyDetail.objects.filter(transfer_info=OuterRef("id")).values("transfer_info").annotate(
            total_price=Sum('price'),
            total_turnover=Sum('turnover'),
        )

        items_to_container = TransferInfo.objects.filter(
            order_item=OuterRef("order_item")).filter(to_detail=f"container-{container_id}").values("order_item").annotate(
                price=Coalesce(
                    Subquery(subq_money_detail.values("total_price")), 0),
                turnover=Coalesce(
                    Subquery(subq_money_detail.values("total_turnover")), 0)
        ).annotate(
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
        ).order_by('order_item')

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
                Q(to_detail=f"container-{container_id}") | Q(
                    to_detail=f"container-{container_id}"),
                order_item=item['order_item']).order_by('created_at')

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


def container_edit_details(request, container_id):
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
