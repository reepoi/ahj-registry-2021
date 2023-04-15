"""TheAHJRegistry URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/

Examples:
    Function views
        #. Add an import:  from my_app import views
        #. Add a URL to urlpatterns:  path('', views.home, name='home')
    Class-based views
        #. Add an import:  from other_app.views import Home
        #. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
    Including another URLconf
        #. Import the include() function: from django.urls import include, path
        #. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('ahj_app.urls')),
    re_path('docs/', include('docs.urls'))
]
