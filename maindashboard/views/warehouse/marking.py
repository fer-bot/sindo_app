from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader

from maindashboard.views.main.user_permissions import permissions
from maindashboard.models import Marking


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.WAREHOUSE_MARKING).first() != None, login_url='/login')
def marking(request):
    if request.method == 'GET':
        markings = Marking.objects.order_by('name')
        context = {
            "markings": markings,
        }
        template = loader.get_template('warehouse/marking/marking.html')
        return HttpResponse(template.render(context, request))


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.WAREHOUSE_MARKING).first() != None, login_url='/login')
def marking_new(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('warehouse/marking/marking_new.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        try:
            name = request.POST["name"]
            description = request.POST["description"]
            newMarking = Marking(name=name, description=description)
            newMarking.save()

            messages.info(
                request, f'Succesfully adding new marking: {name}')
            return redirect('/warehouse/marking')

        except:
            messages.info(
                request, f'Failed! Marking already exist with name: {name}')
            return redirect('/warehouse/marking/new')


@user_passes_test(lambda u: u.is_superuser or u.user_permissions.filter(
    name=permissions.WAREHOUSE_MARKING).first() != None, login_url='/login')
def marking_edit(request, marking_id):
    if request.method == "GET":
        marking = get_object_or_404(Marking, pk=marking_id)

        context = {
            'marking': marking
        }
        template = loader.get_template('warehouse/marking/marking_edit.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        try:
            name = request.POST["name"]
            description = request.POST["description"]
            party = Marking.objects.get(pk=marking_id)
            party.name = name
            party.description = description
            party.save()

            messages.info(
                request, f'Edit is successful!')
            return redirect('/warehouse/marking')
        except:
            messages.info(
                request, f'Edit to marking with id {marking_id} is Unsuccessful! Please make sure the name is unique')
            return redirect(f'/warehouse/marking/edit/{marking_id}')
