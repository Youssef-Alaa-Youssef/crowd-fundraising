
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse
from .models import Users, Activation
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .Forms import Register, LoginForm
from datetime import timedelta
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UsersSerializer
from rest_framework import status

### function for add the user to our website
def AddUser(request):
    if request.method == 'POST':
        form = Register(request.POST, request.FILES)
        if form.is_valid():
            # to start a transcation and tell the database that there is a transcation is happeing but dont commit now #as there some changes are needed before saving
            my_user = form.save(commit=False)
            my_user.image = request.FILES['image']
            form.save()
            #create a record in the activation table for the registered user with activation expires after 24 hrs 
            activation = Activation.objects.create(
                user=my_user, expires_at=timezone.now() + timedelta(hours=24))
            # here we build the activation url with the fill protocl and domain and it calls the activate function with args equal to the token changed into string
            activation_url = request.build_absolute_uri(
                reverse('activate', args=[str(activation.token)]))
            send_mail(
                'Activate your account',
                f'Please click the link below to activate your account:\n{activation_url}',
                'noreply@example.com',
                [my_user.Email],
                fail_silently=False,
            )
            return render(request, 'accounts/Registeration_done.html', {'user': my_user.Firstname, 'email': my_user.Email})
    else:
        form = Register()
    return render(request, "accounts/Signup.html", {'form': form})


def activate(request, token):
    # get the activation using the token sent above when reversing to check if the activation is already expired or not 
    activation = get_object_or_404(Activation, token=token)

    if activation.is_expired():
        activation.delete()
        return HttpResponse("Activation link has expired")
    # if not expired make the user active and authenticated and delete the activation
    user = activation.user
    user.is_active = True
    user.is_authenticated = True
    user.save()
    activation.delete()
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return render(request, 'accounts/Activated.html', {'user': user.Firstname, 'email': user.Email})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # calling our midified authenctiate method in the backends py
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home')
                else:
                    form.add_error(None, 'Your account is inactive, please check your email')
            else:

                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'accounts/Login.html', {'form': form})


@api_view(['GET', 'POST'])
def all_users(request):
    if request.method == 'GET':
        all_users = Users.objects.all()
        users_serializer = UsersSerializer(all_users, many=True)
        return Response(users_serializer.data)
    elif request.method == 'POST':
        user_serializer = UsersSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            user = Users.objects.get(pk=id)
            user.save()
            response_data = user_serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def one_user(request, id):
    one_user = Users.objects.all().get(pk=id)
    if request.method == 'GET':
        ONe_User_Ser = UsersSerializer(one_user, many=False)
        return Response(ONe_User_Ser.data)
    elif request.method == 'PUT':
        one_ser = UsersSerializer(
            data=request.data, instance=one_user)
        if one_ser.is_valid():
            one_ser.save()
            return Response(one_ser.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':
        one_user.delete()
        return Response(status=status.HTTP_202_ACCEPTED)
