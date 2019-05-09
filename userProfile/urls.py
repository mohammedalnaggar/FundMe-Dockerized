from django.urls import path
from . import views



# SET THE NAMESPACE!
app_name = 'userProfile'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns = [
    path('register/', views.register, name='register'),
    path('user_login/', views.user_login, name='user_login'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('create_project/', views.create_project, name='create_project'),
    path('<str:username>/', views.get_user_profile, name='get_user_profile'),
    path('<str:username>/update', views.update_user_profile, name='update_user_profile'),
    path('<str:username>/delete', views.delete_user_profile, name='delete_user_profile'),
    path('<str:username>/donations/', views.get_user_donations, name='user_donations'),
    path('<int:id>/deleteproject', views.delete_user_project, name='delete_user_project'),

]

