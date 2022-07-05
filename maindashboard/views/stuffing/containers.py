from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.db.models import OuterRef, Subquery, Sum, FloatField, ExpressionWrapper, Q, F
from django.db.models.functions import Coalesce

from maindashboard.models import DeliveryParty, Marking, OrderItem, TransferInfo, TransferLogisticDetail


def containers(request):
    if request.method == 'GET':

        containers = TransferLogisticDetail.objects.filter(
            arrived_at__isnull=True).order_by("cabinet_time")
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

        items_to_container = TransferInfo.objects.filter(
            order_item=OuterRef("order_item")).filter(to_detail=f"container-{container_id}").values("order_item").annotate(
            total_box=Sum('order_quantity'),
            total_volume=Sum('volume', output_field=FloatField()),
            total_weight=Sum('weight', output_field=FloatField())
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
        ).order_by('order_item')

        total_box = 0
        total_vol = 0
        total_weight = 0

        for item in items:
            total_box += item["quantity"]
            total_vol += item["volume"]
            total_weight += item["weight"]

            item['item'] = OrderItem.objects.get(pk=item['order_item'])
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
        }
        template = loader.get_template(
            'stuffing/containers/containers_view.html')
        return HttpResponse(template.render(context, request))
