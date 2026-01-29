from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest, FileResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as login_auth, logout
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Exists, OuterRef
from django.core.files.base import ContentFile
from .models import *
from .utils import *
import os
import requests
import re
import base64
import uuid

# Create your views here.
# offdevice views
def index(request):
    requestinfo = PageStartRoutine(request)
    layout = requestinfo["layout"]
    new_communities = list(Community.objects.filter(is_private=False, is_usercreated=False,is_special=False).order_by('-community_id')[:6])
    special_communities = list(Community.objects.filter(is_private=False, is_usercreated=False,is_special=True).order_by('-community_id')[:6])
    usercreated_communities = list(Community.objects.filter(is_private=False, is_usercreated=True,is_special=False).order_by('-community_id')[:6])
    featured_communities = list(Community.objects.filter(is_featured=True).order_by('-community_id')[:4])
    if request.user.is_authenticated:
        mycommfavs = Community_Favorite.objects.filter(user=request.user)[:8]
        if mycommfavs.exists():
            iscomfavs = True
    featured_posts = Post.objects.filter(is_featured=True).order_by('-id')[:10]
    data = {"name":settings.APP_NAME,"IS_PROD":settings.IS_PROD,"ENV_ID":settings.ENV_ID,"use_note":settings.USE_NOTE,"note":settings.NOTE,"new_communities":new_communities,"special_communities":special_communities,"usercreated_communities":usercreated_communities,"featured_communities":featured_communities,"featured_posts":featured_posts,"iscomfavs":iscomfavs,"mycommfavs":mycommfavs}
    return render(request, f"{layout}/indexcommunities.html", data)
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if settings.INVITE_ONLY == True:
            invitecode = request.POST.get("invitecode")
            if not invitecode:
                return HttpResponse("<b>No invite code</b>")
            try:
                invite = Invite.objects.get(InviteCode=invitecode)
            except:
                return HttpResponse("<b>Wrong invite code</b>")
            if invite.MaxJoinCount > invite.JoinCount:
                invite.JoinCount += 1
                invite.save()
            else:
                return HttpResponse("<b>Too many joins from this invite</b>")
        if not username:
            return HttpResponse("<b>No username</b>")
        if User.objects.filter(username=username):
            return HttpResponse("<b>Username taken</b>")
        user = User.objects.create_user(username=username, password=password)
        login_auth(request, user)
        return redirect("/")
    data = {"name":settings.APP_NAME, "action": "Sign Up", "action_description": f"Please create your {settings.APP_NAME} account here.", "is_invite_only": settings.INVITE_ONLY}
    return render(request, "offdevice/signuplogin.html", data)
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login_auth(request, user)
            return redirect("/")
        else:
            return HttpResponse("<b>Incorrect username or password</b>")
    data = {"name":settings.APP_NAME, "action": "Sign In", "action_description": f"Please login into your {settings.APP_NAME} account.", "is_invite_only": settings.INVITE_ONLY}
    return render(request, "offdevice/signuplogin.html", data)
def community(request, olive_title_id, olive_community_id):
    sortby = "all"
    requestinfo = PageStartRoutine(request)
    layout = requestinfo["layout"]
    if request.GET.get("offset"):
        offset = int(request.GET.get("offset"))
    else:
        offset = 0
    nextoffset = offset+50
    if Community.objects.get(olive_community_id=olive_community_id).title:
        title = Title.objects.get(title_id=olive_title_id)
        community = Community.objects.get(title=title, olive_community_id=olive_community_id)
    else:
        community = Community.objects.get(olive_title_id=olive_title_id, olive_community_id=olive_community_id)
    posts = Post.objects.filter(community=community, is_hidden=False).order_by("-id")[offset:offset+50]
    if request.user.is_authenticated:
        is_favorited = Community_Favorite.objects.filter(community=community, user=request.user).exists()
        user_postyeahs = Post_Yeah.objects.filter(post=OuterRef('pk'), user=request.user)
        posts = posts.annotate(is_yeah=Exists(user_postyeahs))
        postyeahs = Post_Yeah.objects.filter(post__in=posts, user=request.user)
        user_postnahs = Post_Nah.objects.filter(post=OuterRef('pk'), user=request.user)
        posts = posts.annotate(is_nah=Exists(user_postnahs))
        postnahs = Post_Nah.objects.filter(post__in=posts, user=request.user)
    else:
        postyeahs = Post_Yeah.objects.filter(post__in=posts)
        
        postnahs = Post_Nah.objects.filter(post__in=posts)
        
    data = {"name":settings.APP_NAME,"IS_PROD":settings.IS_PROD,"ENV_ID":settings.ENV_ID,"ALLOW_SELF_YEAH":settings.ALLOW_SELF_YEAH, "community":community, "posts":posts, "nextoffset": nextoffset, "postyeahs": postyeahs, "postnahs": postnahs, "sortby": sortby, "is_favorited": is_favorited}
    return render(request, f"{layout}/community.html", data)
def posts_endpoint(request):
    if request.method == "POST":
        community = Community.objects.get(olive_title_id=request.POST.get("olv_title_id"), olive_community_id=request.POST.get("olv_community_id"))
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Not logged in!")
        creator = request.user
        feeling = request.POST.get("feeling_id")
        body = request.POST.get("body")
        if len(body) > community.maxpostlength:
            return HttpResponseForbidden("Too long!")
        if community.is_locked == True:
            if not request.user.is_staff:
                return HttpResponseForbidden("You can't post here!")
        is_spoiler = request.POST.get("is_spoiler")
        is_image = False
        if request.POST.get("screenshot"):
            is_image = True
            fdata = base64.b64decode(request.POST.get("screenshot"))
            name = f"{uuid.uuid4().hex}.png"
            file = ContentFile(fdata, name=name)
        else:
            file = ""
        mypost = Post.objects.create(creator=creator, feeling=feeling, community=community, body=body, is_spoiler=bool(is_spoiler), is_image=bool(is_image), image=file, screenshot=request.POST.get("screenshot"))
        data = {"name":settings.APP_NAME, "feeling":feeling,"ALLOW_SELF_YEAH":settings.ALLOW_SELF_YEAH, "body":body, "community": community, "creator": creator, "post": mypost}
        return render(request, "offdevice/posts_endpoint_output.html", data)
@csrf_exempt
def posts_empathies_endpoint(request, id):
    if request.method == "POST":
        if request.user.is_authenticated:
            postobj = Post.objects.get(post_id=id)
            if Post_Yeah.objects.filter(post=postobj, user=request.user).exists():
                return HttpResponseForbidden("Already yeahed with this acc!")
            if Post_Nah.objects.filter(post=postobj, user=request.user).exists():
                return HttpResponseForbidden("Nahed with this acc!")
            if not settings.ALLOW_SELF_YEAH and postobj.creator == request.user:
                return HttpResponseForbidden("This instance blocks self-yeahs!")
            Post_Yeah.objects.create(post=postobj, user=request.user)
            post = Post.objects.get(post_id=id)
            post.yeahs = int(post.yeahs)+1
            post.save()
            userp = post.creator.profile
            userp.karma = int(userp.karma)+1
            userp.save()
            return HttpResponse()
        else:
            return HttpResponseForbidden("Not logged in!")
@csrf_exempt
def posts_empathies_delete_endpoint(request, id):
    if request.method == "POST":
        if request.user.is_authenticated:
            postobj = Post.objects.get(post_id=id)
            if not settings.ALLOW_SELF_YEAH and postobj.creator == request.user:
                return HttpResponseForbidden("This instance blocks self-yeahs!")
            if Post_Yeah.objects.filter(post=postobj, user=request.user).exists():
                Post_Yeah.objects.get(post=postobj, user=request.user).delete()
                post = Post.objects.get(post_id=id)
                post.yeahs = int(post.yeahs)-1
                post.save()
                userp = post.creator.profile
                userp.karma = int(userp.karma)-1
                userp.save()
                return HttpResponse()
            else:
                return HttpResponseForbidden("Not yeahed with this acc!")
        else:
            return HttpResponseForbidden("Not logged in!")
@csrf_exempt
def posts_nahs_endpoint(request, id):
    if request.method == "POST":
        if request.user.is_authenticated:
            postobj = Post.objects.get(post_id=id)
            if not settings.ALLOW_SELF_YEAH and postobj.creator == request.user:
                return HttpResponseForbidden("This instance blocks self-yeahs!")
            if Post_Nah.objects.filter(post=postobj, user=request.user).exists():
                return HttpResponseForbidden("Already nahed with this acc!")
            if Post_Yeah.objects.filter(post=postobj, user=request.user).exists():
                return HttpResponseForbidden("Yeahed with this acc!")
            Post_Nah.objects.create(post=postobj, user=request.user)
            post = Post.objects.get(post_id=id)
            post.nahs = int(post.nahs)+1
            post.save()
            userp = post.creator.profile
            userp.karma = int(userp.karma)-1
            userp.save()
            return HttpResponse()
        else:
            return HttpResponseForbidden("Not logged in!")
@csrf_exempt
def posts_nahs_delete_endpoint(request, id):
    if request.method == "POST":
        if request.user.is_authenticated:
            postobj = Post.objects.get(post_id=id)
            if not settings.ALLOW_SELF_YEAH and postobj.creator == request.user:
                return HttpResponseForbidden("This instance blocks self-yeahs!")
            if Post_Nah.objects.filter(post=postobj, user=request.user).exists():
                Post_Nah.objects.get(post=postobj, user=request.user).delete()
                post = Post.objects.get(post_id=id)
                post.nahs = int(post.nahs)-1
                post.save()
                userp = post.creator.profile
                userp.karma = int(userp.karma)+1
                userp.save()
                return HttpResponse()
            else:
                return HttpResponseForbidden("Not nahed with this acc!")
        else:
            return HttpResponseForbidden("Not logged in!")
def user(request, username):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.user.username == username:
                print(username)
                inuser = User.objects.get(username=username)
                inuser.profile.mii_name = request.POST.get("mii_name", "")
                inuser.profile.bio = request.POST.get("bio", "")
                inuser.profile.pfp_method = request.POST.get("mii_data_type", "")
                inuser.profile.pfp_value = request.POST.get("mii_input", "")
                inuser.save()
                print(username)
                return HttpResponse()
            else:
                return HttpResponseForbidden(f"You aren't {username}, you are {request.user.username}!")
        else:
            return HttpResponseForbidden(f"You aren't logged in!")
    useru = User.objects.get(username=username)
    posts = Post.objects.filter(creator=useru).order_by("-id")
    requestinfo = PageStartRoutine(request)
    layout = requestinfo["layout"]
    if request.GET.get("offset"):
        offset = int(request.GET.get("offset"))
    else:
        offset = 0
    nextoffset = offset+50
    if request.user.is_authenticated:
        user_postyeahs = Post_Yeah.objects.filter(post=OuterRef('pk'), user=request.user)
        posts = posts.annotate(is_yeah=Exists(user_postyeahs))
        postyeahs = Post_Yeah.objects.filter(post__in=posts, user=request.user)
        user_postnahs = Post_Nah.objects.filter(post=OuterRef('pk'), user=request.user)
        posts = posts.annotate(is_nah=Exists(user_postnahs))
        postnahs = Post_Nah.objects.filter(post__in=posts, user=request.user)
    else:
        postyeahs = Post_Yeah.objects.filter(post__in=posts)
        
        postnahs = Post_Nah.objects.filter(post__in=posts)
        
    data = {"name":settings.APP_NAME,"IS_PROD":settings.IS_PROD,"ENV_ID":settings.ENV_ID,"ALLOW_SELF_YEAH":settings.ALLOW_SELF_YEAH, "vuser": useru, "posts": posts, "nextoffset": nextoffset, "postyeahs": postyeahs, "postnahs": postnahs}
    return render(request, f"{layout}/user.html", data)
def post(request, id):
    post = Post.objects.get(post_id=id)
    comments = Comment.objects.filter(post=post)
    requestinfo = PageStartRoutine(request)
    layout = requestinfo["layout"]
    if request.GET.get("offset"):
        offset = int(request.GET.get("offset"))
    else:
        offset = 0
    nextoffset = offset+50
    if request.user.is_authenticated:
        is_yeah = Post_Yeah.objects.filter(post=post, user=request.user).exists()
        is_nah = Post_Nah.objects.filter(post=post, user=request.user).exists()
    else:
        is_yeah = False
        is_nah = False
    if request.user.is_authenticated:
        user_commentyeahs = Comment_Yeah.objects.filter(comment=OuterRef('pk'), user=request.user)
        comments = comments.annotate(is_yeah=Exists(user_commentyeahs))
        commentyeahs = Comment_Yeah.objects.filter(comment__in=comments, user=request.user)
        user_commentnahs = Comment_Nah.objects.filter(comment=OuterRef('pk'), user=request.user)
        commentnahs = Comment_Nah.objects.filter(comment__in=comments, user=request.user)
        comments = comments.annotate(is_nah=Exists(user_commentnahs))
    else:
        commentyeahs = Comment_Yeah.objects.filter(comment__in=comments)
        
        commentnahs = Comment_Nah.objects.filter(comment__in=comments)
        
    data = {"name":settings.APP_NAME,"IS_PROD":settings.IS_PROD,"ENV_ID":settings.ENV_ID,"ALLOW_SELF_YEAH":settings.ALLOW_SELF_YEAH, "post": post, "nextoffset": nextoffset, "is_yeah": is_yeah, "is_nah": is_nah, "comments": comments, "commentyeahs": commentyeahs, "commentnahs": commentnahs}
    return render(request, f"{layout}/post.html", data)
def posts_replies_endpoint(request, id):
    if request.method == "POST":
        post = Post.objects.get(post_id=id)
        post.replies = post.replies+1
        post.save()
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Not logged in!")
        creator = request.user
        feeling = request.POST.get("feeling_id")
        body = request.POST.get("body")
        if len(body) > post.community.maxpostlength:
            return HttpResponseForbidden("Too long!")
        if post.community.allow_comments == False:
            if not request.user.is_staff:
                return HttpResponseForbidden("You can't comment here!")
        is_spoiler = request.POST.get("is_spoiler")
        if request.POST.get("screenshot"):
            fdata = base64.b64decode(request.POST.get("screenshot"))
            name = f"{uuid.uuid4().hex}.png"
            fileimg = ContentFile(fdata, name=name)
        else:
            fileimg = ""
        mycomment = Comment.objects.create(creator=creator, feeling=feeling, post=post, body=body, is_spoiler=bool(is_spoiler), screenshot=request.POST.get("screenshot"), image=fileimg)
        data = {"name":settings.APP_NAME,"ALLOW_SELF_YEAH":settings.ALLOW_SELF_YEAH, "feeling":feeling, "body":body, "community": community, "creator": creator, "post": mycomment}
        return render(request, "offdevice/replies_endpoint_output.html", data)
@csrf_exempt
def replies_empathies_endpoint(request, id):
    if request.method == "POST":
        if request.user.is_authenticated:
            postobj = Comment.objects.get(comment_id=id)
            if not settings.ALLOW_SELF_YEAH and postobj.creator == request.user:
                return HttpResponseForbidden("This instance blocks self-yeahs!")
            if Comment_Yeah.objects.filter(comment=postobj, user=request.user).exists():
                return HttpResponseForbidden("Already yeahed with this acc!")
            if Comment_Nah.objects.filter(comment=postobj, user=request.user).exists():
                return HttpResponseForbidden("Nahed with this acc!")
            Comment_Yeah.objects.create(comment=postobj, user=request.user)
            post = Comment.objects.get(comment_id=id)
            post.yeahs = int(post.yeahs)+1
            post.save()
            userp = post.creator.profile
            userp.karma = int(userp.karma)+1
            userp.save()
            return HttpResponse()
        else:
            return HttpResponseForbidden("Not logged in!")
@csrf_exempt
def replies_empathies_delete_endpoint(request, id):
    if request.method == "POST":
        if request.user.is_authenticated:
            postobj = Comment.objects.get(comment_id=id)
            if not settings.ALLOW_SELF_YEAH and postobj.creator == request.user:
                return HttpResponseForbidden("This instance blocks self-yeahs!")
            if Comment_Yeah.objects.filter(comment=postobj, user=request.user).exists():
                Comment_Yeah.objects.get(comment=postobj, user=request.user).delete()
                post = Comment.objects.get(comment_id=id)
                post.yeahs = int(post.yeahs)-1
                post.save()
                userp = post.creator.profile
                userp.karma = int(userp.karma)-1
                userp.save()
                return HttpResponse()
            else:
                return HttpResponseForbidden("Not yeahed with this acc!")
        else:
            return HttpResponseForbidden("Not logged in!")
def community_hot(request, olive_title_id, olive_community_id):
    sortby = "hot"
    requestinfo = PageStartRoutine(request)
    layout = requestinfo["layout"]
    if request.GET.get("offset"):
        offset = int(request.GET.get("offset"))
    else:
        offset = 0
    nextoffset = offset+50
    community = Community.objects.get(olive_title_id=olive_title_id, olive_community_id=olive_community_id)
    posts = Post.objects.filter(community=community).order_by("-yeahs", "-replies", "nahs")[offset:offset+50]
    if request.user.is_authenticated:
        user_postyeahs = Post_Yeah.objects.filter(post=OuterRef('pk'), user=request.user)
        posts = posts.annotate(is_yeah=Exists(user_postyeahs))
        postyeahs = Post_Yeah.objects.filter(post__in=posts, user=request.user)
        user_postnahs = Post_Nah.objects.filter(post=OuterRef('pk'), user=request.user)
        posts = posts.annotate(is_nah=Exists(user_postnahs))
        postnahs = Post_Nah.objects.filter(post__in=posts, user=request.user)
    else:
        postyeahs = Post_Yeah.objects.filter(post__in=posts)
        
        postnahs = Post_Nah.objects.filter(post__in=posts)
        
    data = {"name":settings.APP_NAME,"IS_PROD":settings.IS_PROD,"ENV_ID":settings.ENV_ID, "community":community, "posts":posts, "nextoffset": nextoffset, "postyeahs": postyeahs, "postnahs": postnahs, "sortby": sortby}
    return render(request, f"{layout}/community.html", data)
def community_cold(request, olive_title_id, olive_community_id):
    sortby = "cold"
    requestinfo = PageStartRoutine(request)
    layout = requestinfo["layout"]
    if request.GET.get("offset"):
        offset = int(request.GET.get("offset"))
    else:
        offset = 0
    nextoffset = offset+50
    community = Community.objects.get(olive_title_id=olive_title_id, olive_community_id=olive_community_id)
    posts = Post.objects.filter(community=community).order_by("yeahs", "replies", "-nahs")[offset:offset+50]
    if request.user.is_authenticated:
        user_postyeahs = Post_Yeah.objects.filter(post=OuterRef('pk'), user=request.user)
        posts = posts.annotate(is_yeah=Exists(user_postyeahs))
        postyeahs = Post_Yeah.objects.filter(post__in=posts, user=request.user)
        user_postnahs = Post_Nah.objects.filter(post=OuterRef('pk'), user=request.user)
        posts = posts.annotate(is_nah=Exists(user_postnahs))
        postnahs = Post_Nah.objects.filter(post__in=posts, user=request.user)
    else:
        postyeahs = Post_Yeah.objects.filter(post__in=posts)
        postnahs = Post_Nah.objects.filter(post__in=posts)
        
    data = {"name":settings.APP_NAME,"IS_PROD":settings.IS_PROD,"ENV_ID":settings.ENV_ID, "community":community, "posts":posts, "nextoffset": nextoffset, "postyeahs": postyeahs, "postnahs": postnahs, "sortby": sortby}
    return render(request, f"{layout}/community.html", data)
def embeddedminjs(request):
    return render(request, "js/embedded.min.js", content_type='application/javascript')
@csrf_exempt
def post_set_spoiler(request, id):
    post = Post.objects.get(post_id=id)
    post.is_spoiler = True
    post.save()
    return HttpResponse()
@csrf_exempt
def post_delete(request, id):
    post = Post.objects.get(post_id=id)
    post.is_hidden = True
    post.save()
    return HttpResponse()

@csrf_exempt
def replies_nahs_endpoint(request, id):
    if request.method == "POST":
        if request.user.is_authenticated:
            postobj = Comment.objects.get(comment_id=id)
            if Comment_Nah.objects.filter(comment=postobj, user=request.user).exists():
                return HttpResponseForbidden("Already nahed with this acc!")
            if Comment_Yeah.objects.filter(comment=postobj, user=request.user).exists():
                return HttpResponseForbidden("Yeahed with this acc!")
            Comment_Nah.objects.create(comment=postobj, user=request.user)
            post = Comment.objects.get(comment_id=id)
            post.nahs = int(post.nahs)+1
            post.save()
            userp = post.creator.profile
            userp.karma = int(userp.karma)-1
            userp.save()
            return HttpResponse()
        else:
            return HttpResponseForbidden("Not logged in!")
@csrf_exempt
def replies_nahs_delete_endpoint(request, id):
    if request.method == "POST":
        if request.user.is_authenticated:
            postobj = Comment.objects.get(comment_id=id)
            if Comment_Nah.objects.filter(comment=postobj, user=request.user).exists():
                Comment_Nah.objects.get(comment=postobj, user=request.user).delete()
                post = Comment.objects.get(comment_id=id)
                post.nahs = int(post.nahs)-1
                post.save()
                userp = post.creator.profile
                userp.karma = int(userp.karma)+1
                userp.save()
                return HttpResponse()
            else:
                return HttpResponseForbidden("Not nahed with this acc!")
        else:
            return HttpResponseForbidden("Not logged in!")
def logoutv(request):
    logout(request)
    return redirect("/")
def toggleneo(request):
    response = redirect("/")
    cookie_age = 10 * 365 * 24 * 60 * 60
    if request.COOKIES.get("layout") == "neo":
        response.delete_cookie("layout")
    else:
        response.set_cookie("layout", "neo", cookie_age)
    return response
def guide_terms(request):
    requestinfo = PageStartRoutine(request)
    layout = requestinfo["layout"]
    data = {"name":settings.APP_NAME,"IS_PROD":settings.IS_PROD,"ENV_ID":settings.ENV_ID}
    return render(request, f"{layout}/guide_terms.html", data)
def guide(request):
    requestinfo = PageStartRoutine(request)
    layout = requestinfo["layout"]
    data = {"name":settings.APP_NAME,"IS_PROD":settings.IS_PROD,"ENV_ID":settings.ENV_ID}
    return render(request, f"{layout}/guide.html", data)
def guide_faq(request):
    requestinfo = PageStartRoutine(request)
    layout = requestinfo["layout"]
    data = {"name":settings.APP_NAME,"IS_PROD":settings.IS_PROD,"ENV_ID":settings.ENV_ID}
    return render(request, f"{layout}/guide_faq.html", data)
def settings_account(request):
    requestinfo = PageStartRoutine(request)
    layout = requestinfo["layout"]
    if not request.user.is_authenticated:
        return redirect("/login")
    data = {"name":settings.APP_NAME,"IS_PROD":settings.IS_PROD,"ENV_ID":settings.ENV_ID}
    return render(request, f"{layout}/profile_settings.html", data)
def create_community(request):
    requestinfo = PageStartRoutine(request)
    layout = requestinfo["layout"]
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == "POST":
        name = request.POST.get("community_name")
        if len(name) > 127:
            return HttpResponseForbidden()
        desc = request.POST.get("community_desc")
        if len(desc) > 255:
            return HttpResponseForbidden()
        if not name:
            return HttpResponseForbidden()
        platform_badge = Platform_Badge.objects.get(id=request.POST.get("platform_badge"))
        platform_name = request.POST.get("platform_name")
        result_community = Community.objects.create(name=name, description=desc, author=request.user, console=platform_badge, platform_name=platform_name, is_usercreated=True)
        return HttpResponse(f"/titles/{result_community.olive_title_id}/{result_community.olive_community_id}")
    data = {"name":settings.APP_NAME,"IS_PROD":settings.IS_PROD,"ENV_ID":settings.ENV_ID,"platform_badges":Platform_Badge.objects.all()}
    return render(request, f"{layout}/create_community.html", data)
@csrf_exempt
def communities_favorite_endpoint(request, olive_title_id, olive_community_id):
    if request.method == "POST":
        if request.user.is_authenticated:
            communityobj = Community.objects.get(olive_title_id=olive_title_id, olive_community_id=olive_community_id)
            if Community_Favorite.objects.filter(community=communityobj, user=request.user).exists():
                return HttpResponseForbidden("Already favorited with this acc!")
            Community_Favorite.objects.create(community=communityobj, user=request.user)
            return HttpResponse()
        else:
            return HttpResponseForbidden("Not logged in!")
@csrf_exempt
def communities_unfavorite_endpoint(request, olive_title_id, olive_community_id):
    if request.method == "POST":
        if request.user.is_authenticated:
            communityobj = Community.objects.get(olive_title_id=olive_title_id, olive_community_id=olive_community_id)
            if Community_Favorite.objects.filter(community=communityobj, user=request.user).exists():
                Community_Favorite.objects.get(community=communityobj, user=request.user).delete()
                return HttpResponse()
            return HttpResponseForbidden("Not favorited!")
        else:
            return HttpResponseForbidden("Not logged in!")
# API views (Kamekverse's custom API, the replica of Miiverse API will be in an extension just like the console UIs)


# Returns basic server config.
def api_server_config(request):
    return JsonResponse({'server_name': settings.APP_NAME, 'is_production': settings.IS_PROD, 'is_development': settings.IS_DEV, 'env_name': settings.ENV_NAME, 'env_id': settings.ENV_ID})