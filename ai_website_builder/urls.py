from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from websites.views import *


urlpatterns = [
    path('', LoginTemplateView.as_view(), name='home'), 
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('preview/<int:website_id>/', preview_website, name='preview_website'),
    path('api/generate/', GenerateWebsiteView.as_view(), name='generate_website'),
    path('api/register/', register_user, name='register_api'),
    path('api/login/', login_user, name='login_api'),
    path('signup/', SignupTemplateView.as_view(), name='signup'),
    path('login/', LoginTemplateView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('website/create/', CreateWebsiteView.as_view(), name='create_website'),
    path('website/edit/<int:pk>/', EditWebsiteView.as_view(), name='edit_website'),
    path('website/delete/<int:pk>/', DeleteWebsiteView.as_view(), name='delete_website'),
    path('logout/', logout_user, name='logout'),
]
