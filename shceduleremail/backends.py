from django.contrib.auth.backends import ModelBackend
from .models import Login
from django.contrib.auth.hashers import *
# from login.util import *

def authenticate(self, request=None, email=None, password=None, **kwars):
    try:
        user = Login.objects.get(email=email)
    except Login.DoesNotExist:
        return None
    if check_password(password, user.password):
        return user
    else:
        return None

def get_user(self, id_login):
    #This shall return the user given the id
    from django.contrib.auth.models import AnonymousUser
    try:
        user = Login.objects.get(id=id_login)
    except Exception as e:
        user = AnonymousUser()
    return user