import re
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Permission, User
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from maindashboard.views.main.user_permissions import permissions
from django.contrib.auth.decorators import user_passes_test


@user_passes_test(lambda u: u.is_superuser)
def users(request):
    if request.method == 'GET':
        User = get_user_model()
        users = User.objects.all()
        user_permissions = []
        for user in users:
            tmp = {}
            tmp["user"] = user
            if user.is_superuser:
                tmp["permission"] = "super user"
            else:
                tmp["permission"] = ', '.join([p.name for p in user.user_permissions.all(
                ) | Permission.objects.filter(group__user=user)])
            user_permissions.append(tmp)

        context = {
            "users": users,
            "permissions": user_permissions,
        }
        template = loader.get_template('admin/users/users.html')
        return HttpResponse(template.render(context, request))


@user_passes_test(lambda u: u.is_superuser)
def users_new(request):
    if request.method == 'GET':
        template = loader.get_template('admin/users/users_new.html')
        return HttpResponse(template.render({}, request))
    if request.method == 'POST':
        try:
            username = request.POST["username"]
            password = request.POST["password"]
            password2 = request.POST["password2"]

            if password != password2:
                messages.info(
                    request, f'Failed! Passwords do not match!')
                return redirect('/admin/users/new')

            user = User.objects.create_user(
                username=username, password=password)
            user.save()
            messages.info(
                request, f'User {username} succesfully created!')
            return redirect('/admin/users')

        except:
            messages.info(
                request, f'Failed! User already exist, Please try again!')
            return redirect('/admin/users/new')


@user_passes_test(lambda u: u.is_superuser)
def users_edit(request, username):
    if request.method == 'GET':
        user = get_object_or_404(User, username=username)
        user_permissions = []

        for p in permissions.permission_list:
            tmp = {}
            tmp["permission"] = p
            tmp["has"] = bool(user.user_permissions.filter(
                name=p).first() != None)
            user_permissions.append(tmp)

        context = {
            "user": user,
            "permissions": user_permissions,
        }
        template = loader.get_template('admin/users/users_edit.html')
        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        user = get_object_or_404(User, username=username)
        newusername = request.POST["username"]
        newemail = request.POST.get("email", None)

        user.username = newusername
        user.email = newemail
        user.user_permissions.clear()

        for p in permissions.permission_list:
            if request.POST.getlist(p):
                user.user_permissions.add(
                    Permission.objects.filter(name=p).first())

        user.save()

        messages.info(
            request, f'User {username} succesfully updated!')
        return redirect('/admin/users')
