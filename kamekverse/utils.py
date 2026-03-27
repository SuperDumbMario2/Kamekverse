from .models import *
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
import hashlib
import secrets
# Page starting routine
def PageStartRoutine(request):
    if request.GET.get("layout") == "neo" or request.COOKIES.get("layout") == "neo":
        layout = "neo"
    else:
        layout = "offdevice"
    return {"layout": layout}
# Do we have access to a community
def IsCommunityAccess(request, community):
    if community.is_private == False:
        return True
    if request.user.is_staff:
        return True
    if request.user.is_authenticated:
        allows = Private_Community_Access.objects.filter(user=request.user, community=community)
        if allows or community.author == request.user:
            return True
    return False
def GetAPIUser(request):
    auth = request.headers.get("Authorization")
    parts = auth.split()
    if len(parts) != 2 or parts[0] != "Bearer":
        return AnonymousUser()
    raw_token = parts[1]
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    try:
        token = API_Token.objects.get(token_hash=token_hash)
        if token.is_usable:
            return token.account
    except API_Token.DoesNotExist:
        return AnonymousUser()
def new_api_key():
    return secrets.token_urlsafe(32)