"""
views of app application
"""

import os,re
from datetime import datetime, timedelta
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.db.models import Count
from .models import *


def page_render(request,page_address,context):
    
    context.__setitem__('easterEgg',True if datetime.now().minute%2==0 else False)
    # operations on elements to add
    app_name = re.split(r'_|(?=[A-Z])', os.path.splitext(os.path.basename(page_address))[0])

    if context['easterEgg']:
        title = ' '.join(word.capitalize() for word in app_name)
    else:
        title= ' '.join(word.lower() for word in app_name)
    
    # appending items to page context
    context.__setitem__('title',str(title))  
    context.__setitem__('year',datetime.now().year)

    return render(
        request,
        page_address,
        context
        )

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return page_render(
        request,
        'app/home.html',
        {'sorted_clubs':Clubs.get_clubs()}
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return page_render(
        request,
        'app/contact.html',
        {
            'message':'Your contact page.',
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return page_render(
        request,
        'app/about.html',
        {
            'message':'Your application description page.',
        }
    )

def club_home(request,club_ID):
    """renders club hompage"""
    assert isinstance(request, HttpRequest)
    return page_render(
        request,
        'BotLaHug/club_home.html',
        Clubs.objects.filter(ID=club_ID).get_club()
        )