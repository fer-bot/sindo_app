from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.template import loader
from django.db.models import OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce

from maindashboard.models import DeliveryParty, Marking, OrderItem, TransferInfo


def delivery_party(request):
    if request.method == 'GET':
        delivery_parties = DeliveryParty.objects.order_by('name')
        context = {
            "delivery_parties": delivery_parties,
        }
        template = loader.get_template(
            'warehouse/delivery_party/delivery_party.html')
        return HttpResponse(template.render(context, request))


def delivery_party_new(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template(
            'warehouse/delivery_party/delivery_party_new.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        try:
            name = request.POST["name"]
            description = request.POST["description"]
            newParty = DeliveryParty(name=name, description=description)
            newParty.save()

            messages.info(
                request, f'Succesfully adding new delivery party: {name}')
            return redirect('/warehouse/delivery_party')

        except:
            messages.info(
                request, f'Failed! delivery party already exist with name: {name}')
            return redirect('/warehouse/delivery_party/new')


def delivery_party_edit(request, party_id):
    if request.method == "GET":
        party = get_object_or_404(DeliveryParty, pk=party_id)

        context = {
            'party': party
        }
        template = loader.get_template(
            'warehouse/delivery_party/delivery_party_edit.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        try:
            name = request.POST["name"]
            description = request.POST["description"]
            party = DeliveryParty.objects.get(pk=party_id)
            party.name = name
            party.description = description
            party.save()

            messages.info(
                request, f'Edit is successful!')
            return redirect('/warehouse/delivery_party')
        except:
            messages.info(
                request, f'Edit to delivery party with id {party_id} is Unsuccessful! Please make sure the name is unique')
            return redirect(f'/warehouse/delivery_party/edit/{party_id}')
