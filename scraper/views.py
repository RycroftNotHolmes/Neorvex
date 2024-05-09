from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Product,Review,Wishlist,Images
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import JsonResponse
from datetime import datetime,timedelta
from decimal import Decimal
from django.contrib.auth.hashers import make_password
from datetime import datetime
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from itertools import zip_longest

def welcome(request):
    if request.method == 'POST':
        action = request.POST.get('')
        if action == 'signup':
            return redirect('signup')
        elif action == 'login':
            return redirect('login')
    return render(request, 'welcome.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        fullname= request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists() :
           return render(request, 'signup.html', {'error_message': 'Username '})

        new_user = User.objects.create(username=username,fullname=fullname, email=email)
        hashed_password = make_password(password)

        new_user.password = hashed_password
        new_user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

        return redirect('home')  # Redirect to the desired page after signup (e.g., home page)

    return render(request, 'signup.html')

def user_login(request):
    if request.method == 'POST':
        print("Request method is POST") 
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user with the provided username and password
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # If authentication is successful, log in the user
            login(request, user)
            return redirect('home')  
        else:
            # If authentication fails, render the login page again with an error message
            return render(request, 'login.html', {'error_message': 'Invalid username or password\n try again'})
    
    # If the request method is not POST, render the login page
    return render(request, 'login.html')


def reset(request):
    return render(request, 'reset.html')

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def search_result(request):
    if request.method == 'POST':
        search_text = request.POST['search_text']
        if search_text:
            search_result = User.objects.filter(username__icontains=search_text)
            return render(request, 'search_result.html', {'search_result': search_result})
        else:
            return render(request, 'search_result.html')
    else:
        return render(request, 'search_result.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def product_page(request):
    if request.method == 'POST':
        product_name = request.POST['product_name']
        product_price = request.POST['product_price']
        product_description = request.POST['product_description']
        product_image = request.FILES['product_image']
        product = Product(product_name=product_name, product_price=product_price, product_description=product_description)
        product_image = Images(product=product,product_image=product_image)
        product.save()
        return redirect('home')
    else:
        return render(request, 'product_page.html')

@login_required
def product_list(request):
    product_list = Product.objects.all()
    return render(request, 'product_list.html', {'product_list': product_list})

@login_required
class profile(LoginRequiredMixin, TemplateView):
    #Profile page view.

    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        #Add user and password change form to the context.
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['password_change_form'] = self.get_password_change_form()
        return context

    def get_password_change_form(self):
        #Return the password change form.
        return PasswordChangeView.get_form_class()(user=self.request.user)

    def post(self, request, *args, **kwargs):
        #Handle password change.
        form = self.get_password_change_form()
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        #Redirect to the profile page after successful password change.
        return super().form_valid(form)

    def form_invalid(self, form):
        #Display form errors.
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        #Return the URL to redirect to after successful password change.
        return reverse_lazy('profile')