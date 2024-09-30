"""
views of bot lahug application clubs views
"""


import os,re
from datetime import datetime, timedelta
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.db.models import Count
from app import models



def page_render(request,page_address,context,club_name):
    
    context.__setitem__('easterEgg',True if datetime.now().minute%2==0 else False)
    # operations on elements to add
    app_name = re.split(r'_|(?=[A-Z])', os.path.splitext(os.path.basename(page_address))[0])

    if context['easterEgg']:
        title = ' '.join(word.capitalize() for word in app_name)
    else:
        title= ' '.join(word.lower() for word in app_name)
    
    # appending items to page context
    context.__setitem__('name',club_name)  
    context.__setitem__('title',str(title))  
    context.__setitem__('year',datetime.now().year)

    return render(
        request,
        page_address,
        context
        )

def contact(request,club_name):
    """Renders the club contact page."""
    club =  get_object_or_404(models.Clubs,web_name=club_name)
    details = club.get_club()
    assert isinstance(request, HttpRequest)
    return page_render(
        request,
        'BotLaHug/contact.html',
        details,
        club_name=club_name
    )

def home(request, club_name):
    """
    Renders the club home page with all necessary information such as club details and associated articles.
    
    Args:
        request (HttpRequest): The HTTP request object.
        club_name (str): The web_name of the club used to retrieve the specific club instance.

    Returns:
        HttpResponse: Rendered club home page with details and articles.
    """
    
    club = get_object_or_404(models.Clubs, web_name=club_name)
    articles = models.Article.objects.filter(club=club)

    # Prepare a dictionary of articles with relevant information
    club_articles = {}
    for article in articles:
        image = models.Images.objects.filter(club=club, page='Articles', name=article.title).first()
        club_articles[article.title] = {
            'ID': article.ID,
            'image': image.image.url if image else None,
            'description': article.content[:100],  # Short description of the article
            'publication_date': article.publication_date,
            'web_name': article.ID  # Use article ID for URL
        }

    # Fetch club details
    details = club.get_club()

    # Render the club home page with club details and articles
    return page_render(
        request,
        'BotLaHug/club_home.html',
        {
            'details': details,
            'articles': club_articles
        },
        club_name=club_name
    )

def article(request,club_name,article_ID):
    """
    Renders the article page with detailed information about the selected article.
    
    Args:
        request (HttpRequest): The HTTP request object.
        article_id (int): The ID of the article used to retrieve the specific article instance.

    Returns:
        HttpResponse: Rendered article page with details and related articles.
    """
    
    article = get_object_or_404(models.Article, ID=article_ID)
    related_articles = models.Article.objects.filter(club=article.club).exclude(ID=article_ID)
    article_images = models.Images.get_images_for_page(club=article.club, page='Articles', name=article.title)

    article_details = {
        'ID':article_ID,
        'title': article.title,
        'content': article.content,
        'publication_date': article.publication_date,
        'image': article_images if article_images else None  
        }

    return page_render(
        request,
        'BotLaHug/article.html',
        {
            'article_details': article_details,
            'related_articles': related_articles
        },
        club_name=club_name
    )

def athlete_profile(request,club_name, athlete_id):
    """
    Renders the athlete profile page with all necessary information such as profile picture, contact info, etc.
    
    Args:
        request (HttpRequest): The HTTP request object.
        athlete_id (str): The unique ID of the athlete.
    
    Returns:
        HttpResponse: Rendered athlete profile page.
    """
    
    athlete = get_object_or_404(models.Athlete, ID=athlete_id)
    
    return page_render(
        request, 
        'BotLaHug/athlete_profile.html', 
        {'athlete': athlete},
        club_name=club_name
        )

def club_athletes(request, club_name):
    """
    Renders the athletes page displaying all athletes for a specific club.
    
    Args:
        request (HttpRequest): The HTTP request object.
        club_id (int): The ID of the club to fetch athletes for.

    Returns:
        HttpResponse: Rendered athletes page with the list of athletes for the specified club.
    """
    
    club = get_object_or_404(models.Clubs, web_name=club_name)
    
    athletes = club.athletes.all()  
    
    return page_render(
        request, 
        'BotLaHug/club_athletes.html', 
        {
            'club': club, 
            'athletes': athletes
        },
        club_name=club_name

    )