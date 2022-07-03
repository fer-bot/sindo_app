from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.template import loader
from django.db.models import OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce

from maindashboard.models import DeliveryParty, Marking, OrderItem, TransferInfo

# Create your views here.


def home(request):
    if request.method == 'GET':
        return redirect('/dashboard')


def dashboard(request):
    if request.method == 'GET':
        template = loader.get_template('dashboard.html')
        return HttpResponse(template.render({}, request))