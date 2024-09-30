from django.contrib import admin

from .models import *

models= [
    Clubs,
    Topics,
    Design,
    topic_relations,
    Images,
    Article,
    Season,
    Athlete,
]
for model in models:
    admin.site.register(model)

# Register your models here.
