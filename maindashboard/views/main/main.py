from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.template import loader


from maindashboard.models import DeliveryParty, Marking, OrderItem, TransferInfo

# Create your views here.


@login_required(login_url='/login')
def home(request):
    if request.method == 'GET':
        return redirect('/dashboard')


@login_required(login_url='/login')
def dashboard(request):
    if request.method == 'GET':
        template = loader.get_template('main/dashboard.html')
        return HttpResponse(template.render({}, request))


def login_page(request):
    if request.method == 'GET':
        template = loader.get_template('main/login.html')
        return HttpResponse(template.render({}, request))
    if request.method == 'POST':
        try:
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)

            if user is None:
                messages.info(
                    request, f'Login failed! please recheck your username and password!')
                return redirect('/login')

            login(request, user)
            return redirect('/')
        except:
            messages.info(
                request, f'Login failed! please recheck your username and passwords!')
            return redirect('/login')
