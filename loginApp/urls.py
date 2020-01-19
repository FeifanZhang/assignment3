from loginApp import views
from django.urls import include, path

urlpatterns = [

    path('login/',views.login,name="login"),
    path('register/',views.register,name="register"),
    path('registerpage/',views.registerpage,name="registerpage"),
    path('returnToLoginpage/',views.returnToLoginpage,name="returnToLoginpage"),
]