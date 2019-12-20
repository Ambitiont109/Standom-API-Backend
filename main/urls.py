"""main App URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, include
from main import views
from django.views.generic import RedirectView
# from django.core.urlresolvers import reverse_lazy
app_name = 'main'

urlpatterns = [
    # Authentication
    # path('', RedirectView.as_view(url='list/user/', permanent=True)),    
    path('login/', views.loginApi),
    path('admin/logout/', views.logout_view),
    path('admin/login/', views.login_view),
    path('register/', views.register),
    path('list/question/', views.list_question),
    path('list/user/', views.list_user),
    path('update/user/', views.update_user),
    path('check_answer/', views.check_answer),
    path('users/list', views.UserListView.as_view(), name='list_user'),
    path('users/create', views.UserCreateView.as_view(), name='add_user'),
    path('users/update/<int:pk>', views.UserUpdateView.as_view(), name='update_user'),
    path('users/delete/<int:pk>', views.delete_user_view, name='delete_user'),
    path('users/detail/<int:pk>', views.detail_user_view, name='detail_user'),
    path('answers/detail/<int:pk>', views.detail_answer_view, name='detail_answer'),
    path('',views.login_view),
]
