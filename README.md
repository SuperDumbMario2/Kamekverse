# Kamekverse
This is still in early development.

## How to set up

First install everything in deps.txt into your venv.

`pip install -r deps.txt`

Then, build the database.

`python manage.py makemigrations`

`python manage.py migrate`

Set up settings.py (put a private key instead of the django default that was on my localhost instance, make debug false, set up the enviroment parameters, and other stuff)

Collect static:

`python manage.py collectstatic`

Make a superuser:

`python manage.py createsuperuser`

Run server (if localhosting):

`python manage.py runserver`

Log into the superuser acc, go to [kamekverse instance domain, 127.0.0.1:8000 if you're localhosting]/admin/, create an platform badge so the communities' platform badge settings not glitch out. You can use an empty image.

Once you did this, it's mostly complete. Create communities, add themes, etc.
