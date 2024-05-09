from . import views
from django.urls import path

urlpatterns = [
    path('welcome/', views.welcome, name='welcome'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('reset/', views.reset, name='reset'),
    
    path('home/',views.home, name='home'),
    path('search_result/',views.search_result, name='search_result'),
    path('product_page',views.product_page, name='product_page'),
    path('profile/', views.profile, name='profile')
    
]