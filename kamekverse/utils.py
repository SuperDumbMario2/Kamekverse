from .models import *
from django.conf import settings
# Page starting routine
def PageStartRoutine(request):
    if request.GET.get("layout") == "neo" or request.COOKIES.get("layout") == "neo":
        layout = "neo"
    else:
        layout = "offdevice"
    return {"layout": layout}