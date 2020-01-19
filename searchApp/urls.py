
from searchApp import views
from django.urls import include, path

urlpatterns = [

    path('index/',views.index,name="index"),
    path('back/',views.back,name="back"),
    path('download/',views.download,name="download"),
    path('save/', views.save, name="save"),
    path('delete/',views.delete,name='delete'),
    path('cancellation/',views.cancellation,name="cancellation"),
]