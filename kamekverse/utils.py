from .models import *
from django.conf import settings
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