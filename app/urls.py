from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import login, logout
from eyetracking.views import index, upload_image


urlpatterns = [
    path('', index),
    path('upload/', upload_image),
    path('accounts/login/', login),
    path('accounts/logout/', logout),
    path('admin/', admin.site.urls),
]
