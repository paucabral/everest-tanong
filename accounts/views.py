from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from .forms import CreateUserForm, ProfileForm, CreateSuperUserForm
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import make_password
from .decorators import *

# Create your views here.


class Login(View):
    @method_decorator(unauthenticated_user)
    def get(self, request, *args, **kwargs):
        return render(request, template_name='accounts/login.html', context={})

    @method_decorator(unauthenticated_user)
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('/administrator/dashboard')
            else:
                return redirect('/member/dashboard')
        else:
            messages.info(request, 'Username or Password is incorrect.')
        return render(request, template_name='accounts/login.html', context={})


@login_required(login_url='/')
def logoutUser(request):
    logout(request)
    return redirect('/')


class Register(View):
    @method_decorator(unauthenticated_user)
    def get(self, request, *args, **kwargs):
        form = CreateUserForm()
        return render(request, template_name='accounts/register.html', context={'form': form})

    @method_decorator(unauthenticated_user)
    def post(self, request, *args, **kwargs):
        form = CreateUserForm(request.POST)

        if form.is_valid():
            user = form.save()

            profile = Profile(user=user)
            profile.save()
            return redirect('/registration-success/')

        else:
            messages.error(request, 'There was an error.')
        return render(request, template_name='accounts/register.html', context={'form': form})


class RegistrationSuccess(View):
    @method_decorator(unauthenticated_user)
    def get(self, request, *args, **kwargs):
        return render(request, template_name='accounts/registration-success.html', context={})


class AccountProfile(View):
    @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.get(user=user)

        form = ProfileForm(instance=profile)

        return render(request, template_name='accounts/profile.html', context={'form': form})

    @method_decorator(login_required(login_url='/'))
    def post(self, request, *args, **kwargs):
        user = request.user
        user_instance = Profile.objects.get(user=user)
        account_instance = User.objects.get(id=user.id)

        form = ProfileForm(request.POST, request.FILES, instance=user_instance)

        if form.is_valid():
            form.save()

            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            email = request.POST["email"]
            username = request.POST["username"]

            account_instance.first_name = first_name
            account_instance.last_name = last_name
            account_instance.email = email
            account_instance.username = username

            account_instance.save()

            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Your profile information was saved successfully.')

            return redirect("/profile")

        else:
            messages.error(
                request, 'There was an error saving in your profile information.')
        return redirect("/profile")


class AccountProfileAdmin(View):
    @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.get(user=user)

        form = ProfileForm(instance=profile)

        return render(request, template_name='accounts/profile-admin.html', context={'form': form})

    @method_decorator(login_required(login_url='/'))
    def post(self, request, *args, **kwargs):
        user = request.user
        user_instance = Profile.objects.get(user=user)
        account_instance = User.objects.get(id=user.id)

        form = ProfileForm(request.POST, request.FILES, instance=user_instance)

        if form.is_valid():
            form.save()

            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            email = request.POST["email"]
            username = request.POST["username"]

            account_instance.first_name = first_name
            account_instance.last_name = last_name
            account_instance.email = email
            account_instance.username = username

            account_instance.save()

            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Your profile information was saved successfully.')

            return redirect("/administrator/admin-profile")

        else:
            messages.error(
                request, 'There was an error saving in your profile information.')
        return redirect("/profile")


class AdminRegisterSuperuser(View):
    @method_decorator(login_required(login_url='/'))
    @method_decorator(admin_only())
    def get(self, request, *args, **kwargs):
        tmp_password = make_password('')
        form = CreateSuperUserForm(
            initial={'password1': tmp_password, 'password2': tmp_password, 'is_superuser': True, 'is_staff': True})
        form.fields['password1'].widget.render_value = True
        form.fields['password2'].widget.render_value = True
        form.fields['is_superuser'].widget.render_value = True
        form.fields['is_staff'].widget.render_value = True

        staffs = User.objects.filter(is_superuser=True).filter(is_staff=True)

        return render(request, template_name='accounts/admin-register-staff-account.html', context={'form': form, 'staffs': staffs})

    @method_decorator(login_required(login_url='/'))
    @method_decorator(admin_only())
    def post(self, request, *args, **kwargs):
        form = CreateSuperUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            profile = Profile(user=user)
            profile.save()

            messages.add_message(request,
                                 messages.SUCCESS,
                                 'The administrator account was registered successfully.')
            return redirect("/administrator/staff")
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'There was an error in creating the account.')
        return redirect("/administrator/staff")


@login_required(login_url='/')
@admin_only()
def deleteStaff(request, staff_id):
    if request.method == "POST":
        user = User.objects.filter(id=staff_id)
        user.delete()

        messages.add_message(request,
                             messages.SUCCESS,
                             'The administrator account was deleted successfully.')
        return redirect('/administrator/staff')

    return redirect('/administrator/staff')
