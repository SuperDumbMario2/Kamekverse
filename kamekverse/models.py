from django.db import models
from django.core.validators import *
from django.contrib.auth.models import User
from django.conf import settings
import random
import base64
import uuid
import os

# Create your models here.
def olive_ids():
    return random.randint(6400000000000000000, 6499999999999999999)
def post_ids():
    # Original Miiverse started post IDs with "AYED"/018101 on dev and with "AYMH"/018307 on prod, also I found posts with IDs starting with "AYQB"/018401 in a leaked Debug warawara plaza directory (if you want it, use JNusTool to download v24 of any region's Wii U Menu, it will have it.)
    # This is an attempt on rewriting Grape code for ID generation. Even tho grape is not a very good codebase, it's ID gen is pretty nice
    if settings.IS_PROD == False:
        magic1 = b"\x01\x81\x01"
    else:
        magic1 = b"\x01\x83\x07"
    urlenv = b"\x00\x00" # padding or smth idk
    magic2 = b"\x41" # another magic
    randbytes = random.getrandbits(80).to_bytes(10, "big")
    return base64.urlsafe_b64encode(magic1+urlenv+magic2+randbytes).decode('utf-8').rstrip('=')
    """if settings.IS_PROD == True:
        return "AYMH"+''.join(random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for i in range(18))
    else:
        return "AYED"+''.join(random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for i in range(18))"""
    #return "AYMHAAA"+''.join(random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for i in range(15))
def themeurls(instance, filename):
    if not instance.pk:
        instance._folder_name = uuid.uuid4().hex
    folder = getattr(instance, "_folder_name", None) or instance.tid or "default"
    return os.path.join("themecss", folder, filename)
class Platform_Badge(models.Model):
    img = models.ImageField(upload_to="community_flair_icons/", default="community_flair_icons/null.png") # Image
    name = models.CharField(max_length=127, default="Unnamed Badge") # Internal name, used for admin panel
    def __str__(self):
        return self.name
class Title(models.Model):
    name = models.CharField(max_length=127) # Title name
    title_id = models.BigIntegerField(default=olive_ids) # Title ID, uses placeholder/random ID
    offdevice_icon = models.ImageField(upload_to="title_icons/", default="community_icons/default.png") # offdevice icon for this title
    offdevice_banner = models.ImageField(upload_to="title_banners/", null=True, blank=True) # default offdevice banner for this title
    console = models.ForeignKey(Platform_Badge, on_delete=models.SET_NULL, null=True, blank=True, default=1)# The console badge
    platform_name = models.TextField(null=True, blank=True) # The platform name
    def __str__(self):
        return self.name
class Theme(models.Model):
    name = models.TextField() # Theme name
    tid = models.TextField(default=post_ids) # Theme ID
    css = models.FileField(upload_to=themeurls) # Main CSS file of the theme
    def __str__(self):
        return self.name
class Community(models.Model):
    name = models.CharField(max_length=127) # community name
    olive_community_id = models.TextField(default=olive_ids) # URL community id
    olive_title_id = models.TextField(default=0) # title id, i am phasing this method of passing title ids out but keeping it to not break shit.
    title = models.ForeignKey(Title, on_delete=models.CASCADE, null=True, blank=True) # Title that the community belongs to.
    community_id = models.AutoField(primary_key=True) # API community id, i'd start from 1000 beacuse i saw that the "Miiverse Official Community Tool" thing for 3ds that was used to create communities in past before MMAS but Django is being a retard and doesn't let me to do that
    description = models.CharField(max_length=255, null=True, blank=True) # community description
    is_private = models.BooleanField(default=False) # Is the community private? If yes, then it will be whitelisted.
    is_locked = models.BooleanField(default=False) # Is the community locked? If yes, the only people who can post there are admins and whitelisted users.
    is_redesigned = models.BooleanField(default=False) # Will the community use the features of the redesign Miiverse?
    appdata = models.BinaryField(null=True, blank=True) # Application data. As of writing this, I am not sure how it exactly behaves but it's usually saved as a bin file so it's a binary field.
    block_swears = models.BooleanField(default=False) # if true block swear words on the community
    #console = models.TextField(null=True, blank=True) # The console badge
    console = models.ForeignKey(Platform_Badge, on_delete=models.SET_NULL, null=True, blank=True, default=1)# The console badge
    has_badge = models.BooleanField(default=False) # Does the community have a blue badge?
    badge = models.TextField(null=True, blank=True) # the blue badge
    platform_name = models.TextField(null=True, blank=True) # The platform name
    maxpostlength = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(2200)], default=2200) # Max post length for this community. 400 in some cases
    maxcommentlength = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(2200)], default=2200) # Max comment length for this community.' 400 in some cases
    offdevice_icon = models.ImageField(upload_to="community_icons/", default="community_icons/default.png") # offdevice icon for this community
    offdevice_banner = models.ImageField(upload_to="community_banners/", null=True, blank=True) # offdevice banner for this community
    is_usercreated = models.BooleanField(default=False) # Is the community created by an user?
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # Author ID for the community (if user created)
    is_special = models.BooleanField(default=False) # Is the community displayed in the special tab?
    is_featured = models.BooleanField(default=False) # Is the community featured?
    allow_comments = models.BooleanField(default=True) # Does the community allow comments?
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Communities"
class Post(models.Model):
    post_id = models.TextField(default=post_ids) # URL post ID
    creator = models.ForeignKey(User, on_delete=models.CASCADE) # creator
    community = models.ForeignKey(Community, on_delete=models.CASCADE) # community
    body = models.CharField(max_length=2200, null=True, blank=True) # the post body
    yeahs = models.IntegerField(default=0) # Yeah amount
    nahs = models.IntegerField(default=0) # Nah amount
    replies = models.IntegerField(default=0) # reply amount
    feeling = models.TextField(default="normal") # Feeling'
    is_spoiler = models.BooleanField(default=False) # Is it a spoiler?
    creation_date = models.DateTimeField(auto_now_add=True)# Date of the post's creation
    is_image = models.BooleanField(default=False) # Used for the sampler so it will not be that the sampler placeholder is pinned to everything
    image = models.ImageField(upload_to="post_images/", default="post_images/sampler_placeholder.png") # An image
    screenshot = models.TextField(null=True, blank=True) # b64 screenshot value. Kept for Miiverse accuracy
    post_file = models.ImageField(upload_to="post_files/", null=True, blank=True) # Other file types
    is_featured = models.BooleanField(default=False) # Is the post featured AKA used on the homepage sampler?
    is_hidden = models.BooleanField(default=False) # Is the post hidden?
    is_multilanguage = models.BooleanField(default=False) # Is the post multilanguage?
    # The fields below are multilang post bodies
    body_0 = models.CharField(max_length=2200, null=True, blank=True)
    body_1 = models.CharField(max_length=2200, null=True, blank=True)
    body_2 = models.CharField(max_length=2200, null=True, blank=True)
    body_3 = models.CharField(max_length=2200, null=True, blank=True)
    body_4 = models.CharField(max_length=2200, null=True, blank=True)
    body_5 = models.CharField(max_length=2200, null=True, blank=True)
    body_6 = models.CharField(max_length=2200, null=True, blank=True)
    body_7 = models.CharField(max_length=2200, null=True, blank=True)
    body_8 = models.CharField(max_length=2200, null=True, blank=True)
    body_9 = models.CharField(max_length=2200, null=True, blank=True)
    body_10 = models.CharField(max_length=2200, null=True, blank=True)
    def __str__(self):
        return f"{self.creator.profile.mii_name}'s post ({self.body})"
class Invite(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE) # Who made the invite
    MaxJoinCount = models.IntegerField(default=1) # How many people can join from the invite?
    JoinCount = models.IntegerField(default=0) # How many people joined?
    InviteCode = models.UUIDField(default=uuid.uuid4, unique=True) # Code for the invite
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pfp_method = models.TextField(null=True, blank=True) # Method of getting the pfp (if we use a mii from a nnid it should be 'mii-nnid', if we use a mii from pnid it should be 'mii-pnid', if we use raw mii data it should be 'mii-ariankordi', if it's the placeholder pfp it should be anything else or null.)
    pfp_value = models.TextField(null=True, blank=True) # if a mii will be used, nnid/pnid/raw data falls here
    mii_name = models.CharField(max_length=127, null=True, blank=True) # Mii name/display name.
    bio = models.CharField(max_length=2200, null=True, blank=True) # Profile comment/bio
    follower_count = models.IntegerField(default=0) # Follower count, for the sake of not having to pull out the follower data to count the followers.
    friend_count = models.IntegerField(default=0) # friend count
    follow_count = models.IntegerField(default=0) # Follow count, for the sake of not having to pull out the follow data to count the follows.
    game_experience = models.TextField(default="beginner") # Game experience.
    post_count = models.IntegerField(default=0) # Post count
    yeah_count = models.IntegerField(default=0) # Amount of yeahs this user has given
    karma = models.IntegerField(default=0) # Amount of Mii Coins this user has.
    featured_post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True) # What is the post shown on the user's banner?
    discord = models.TextField(null=True, blank=True) # Discord tag
    ban = models.BooleanField(default=False) # Is banned?
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True, blank=True)
    themecolor = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.user.username
class Post_Yeah(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
class Post_Nah(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
class Comment(models.Model):
    comment_id = models.TextField(default=post_ids) # URL comment ID
    creator = models.ForeignKey(User, on_delete=models.CASCADE) # creator
    post = models.ForeignKey(Post, on_delete=models.CASCADE) # post
    body = models.CharField(max_length=400) # the post body
    yeahs = models.IntegerField(default=0) # Yeah amount
    nahs = models.IntegerField(default=0) # Nah amount
    replies = models.IntegerField(default=0) # reply amount
    feeling = models.TextField(default="normal") # Feeling'
    is_spoiler = models.BooleanField(default=False) # Is it a spoiler?
    creation_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="comment_images/", null=True, blank=True) # An image
    screenshot = models.TextField(null=True, blank=True) # b64 screenshot value. Kept for Miiverse accuracy
    post_file = models.ImageField(upload_to="post_files/", null=True, blank=True) # Other file types
class Comment_Yeah(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
class Comment_Nah(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)