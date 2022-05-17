from django.urls import path
from .views import home, signup, signin, signout, activate

urlpatterns = [
    path('', home, name='home'),
    path('signup', signup, name='signup'),
    path('signin', signin, name='signin'),
    path('signout', signout, name='signout'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
]