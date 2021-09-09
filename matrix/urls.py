"""matrix URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from matrix_web import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('api/', include('matrix_web.urls')),
    path('login/auth/', auth_views.LoginView.as_view(template_name='login/login.html'), name='login_auth'),
    path('logout/auth/', auth_views.LogoutView.as_view(template_name='login/login.html'), name='logout_auth'),
    path('control/', views.control, name='control'),
    path('kvm/', views.kvm, name='kvm'),
    path('profile_control/', views.profile_control, name='profile_control'),
    path('system_template/', views.system_template, name='system_template'),
    path('profile_template/', views.profile_template, name='profile_template'),
    path('test/', views.test, name='test'),
]