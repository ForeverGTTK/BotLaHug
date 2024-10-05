"""
views of bot lahug application clubs views
"""


import os,re
from datetime import time, datetime, timedelta, date  
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.db.models import Count
from collections import defaultdict
from app import models



def page_render(request, page_address, context, club_name):
    """
    Renders a page with updated context data, including a dynamically generated title and an optional 'easterEgg' feature.

    Args:
        request (HttpRequest): The HTTP request object.
        page_address (str): Path to the template file.
        context (dict): Context data to be passed to the template.
        club_name (str): Name of the club, added to the context.

  
    Returns:
        HttpResponse: The rendered page with the updated context.

  """
    context['easterEgg'] = datetime.now().minute % 2 == 0
    
    app_name = re.split(r'_|(?=[A-Z])', os.path.splitext(os.path.basename(page_address))[0])
    title = ' '.join(word.capitalize() if context['easterEgg'] else word.lower() for word in app_name)
    
    context.update(
        {
            'name': club_name, 
            'title': title, 
            'year': datetime.now().year, 
        }
    )
    
    return render(request, page_address, context)

def about(request, club_name):
    club = get_object_or_404(models.Clubs, web_name=club_name)
    
    # Fetch the current season
    current_season = models.Season.objects.filter(club=club, is_active=True).first()
    class_count = models.Class.objects.filter(season=current_season).count() if current_season else 0
    season_count = models.Season.objects.filter(club=club).count()
    athlete_count = models.Athlete.objects.filter(club=club).count()
    
    classes = models.Class.objects.filter(season=current_season) if current_season else []
    total_classes_days = sum([len(c.days_of_week) for c in classes])
    average_training_per_week = total_classes_days // athlete_count if athlete_count > 0 else 0

    context = {
        'club': club,
        'current_season': current_season,
        'class_count': class_count,
        'season_count': season_count,
        'athlete_count': athlete_count,
        'average_training_per_week': average_training_per_week,
        'classes': classes,
    }
    
    return page_render(request, 'BotLaHug/client_pages/about.html', context, club_name=club_name
)

def contact(request,club_name):
    """Renders the club contact page."""
    club =  get_object_or_404(models.Clubs,web_name=club_name)
    details = club.get_club()
    assert isinstance(request, HttpRequest)
    return page_render(
        request,
        'BotLaHug/client_pages/contact.html',
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
    club_articles = {}
    for article in articles:
        image = models.Images.objects.filter(club=club, page='Articles', name=article.title).first()
        club_articles[article.title] = {
            'ID': article.ID,
            'image': image.image.url if image else None,
            'description': article.content[:100],
            'publication_date': article.publication_date,
            'web_name': article.ID 
            
        }

    details = club.get_club()
    classes = models.Class.get_classes_by_current_season(club=club)
    days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    schedule_classes = generate_time_slots(classes, days_of_week)
    
    features = models.Features.objects.filter(club_ID=club)
    feature_data = {feature.title:feature.get_club_fields() for feature in features}
    
    future = feature_data.pop('Future', None)
    if future:
        feature_data['Future'] = future
    return page_render(
        request,
        'BotLaHug/client_pages/club_home.html',
        {
            'details': details,
            'articles': club_articles,
            'schedule_classes': schedule_classes,
            'days_of_week': days_of_week,
            'features': feature_data,

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
        'BotLaHug/client_pages/article.html',
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
        'BotLaHug/club_pages/athlete_profile.html', 
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
        'BotLaHug/club_pages/club_athletes.html', 
        {
            'club': club, 
            'athletes': athletes
        },
        club_name=club_name

    )

def find_athlete(request, club_name):
    """
    Renders the find athlete page and processes the search request for an athlete.
    
    Args:
        request (HttpRequest): The HTTP request object.
        club_name (str): The web_name of the club used to retrieve the specific club instance.

    Returns:
        HttpResponse: Redirects to the athlete profile page if found, otherwise renders the find athlete page.
    """
    club = get_object_or_404(models.Clubs, web_name=club_name)

    # If the form is submitted (GET request with athlete_id)
    if 'athlete_id' in request.GET:
        athlete_id = request.GET.get('athlete_id')
        
        # Try to find the athlete by ID within the specified club
        try:
            athlete = models.Athlete.objects.get(athlete_id=athlete_id, club=club)
            # Redirect to the athlete's profile page
            return redirect('athlete_profile', club_name=club_name, athlete_id=athlete.ID)
        except models.Athlete.DoesNotExist:
            # If the athlete is not found, render the same page with an error message
            context = {
                'club_logo_url': club.get_club().get('photo'),
                'club_name': club.name,
                'error_message': 'Athlete not found. Please check the ID and try again.'
            }
            return page_render(
                request, 
                'BotLaHug/client_pages/find_athlete.html', 
                context,
                club_name=club_name
            )

    context = {
        'club_logo_url': club.get_club().get('photo').image.url,
    }

    return page_render(
        request, 
        'BotLaHug/client_pages/find_athlete.html', 
        context,
        club_name=club_name
    )

def club_classes(request, club_name):
    """
    Renders the classes page displaying all classes for a specific club.
    
    Args:
        request (HttpRequest): The HTTP request object.
        club_name (str): The web_name of the club to fetch classes for.

    Returns:
        HttpResponse: Rendered classes page with the list of classes for the specified club.
    """
    
    club = get_object_or_404(models.Clubs, web_name=club_name)
    
    classes = models.Class.get_classes_by_current_season(club)
    
    return page_render(
        request, 
        'BotLaHug/club_pages/club_classes.html', 
        {
            'classes': classes
        },
        club_name=club_name
    )

def class_info(request, club_name, class_id):
    """
    Renders the class information page with all necessary details such as schedule, teacher, location, etc.
    
    Args:
        request (HttpRequest): The HTTP request object.
        class_id (str): The unique ID of the class.
    
    Returns:
        HttpResponse: Rendered class information page.
    """
    club = models.Clubs.objects.get(web_name=club_name)
    # Fetch the class based on the class_id
    class_instance = get_object_or_404(models.Class, ID=class_id)
    
    # Prepare class details
    class_details = {
        'name': class_instance.name,
        'season': class_instance.season,
        'start_date': class_instance.start_date,
        'end_date': class_instance.end_date,
        'days_of_week': class_instance.days_of_week,
        'start_time': class_instance.start_time.strftime('%H:%M'),
        'end_time': class_instance.end_time.strftime('%H:%M'),
        'teacher': class_instance.teacher,
        'place': class_instance.place,
        'price': class_instance.price,
        'registration_fee': class_instance.registration_fee,
        'club_logo_url': club.get_club().get('photo'),

    }
    
    # Additional tools or options that might be available
    tools = {
        'edit': 'Edit Class Details',
        'register': 'Register New Athlete',
        'manage': 'Manage Class Registrations',
    }
    
    return page_render(
        request,
        'BotLaHug/client_pages/class_info.html',
        {
            'class_details': class_details,
            'tools': tools,
        },
        club_name=club_name
    )

def club_class_info(request, club_name, class_id):
    """
    Renders the class information page, displaying registered users and class details.

    Args:
        request (HttpRequest): The HTTP request object.
        club_name (str): The name of the club.
        class_id (str): The ID of the class.
    
    Returns:
        HttpResponse: Rendered class information page with registered athletes and stats.
    """
    class_instance = get_object_or_404(models.Class, ID=class_id)
    registrations = models.Registration.objects.filter(class_id=class_instance.ID)    
    athletes = [reg.athlete for reg in registrations]
    total_athletes = registrations.count()

    context = {
        'class_details': class_instance,
        'total_athletes': total_athletes,
        'athletes': athletes,
        'club_name': club_name
    }

    return page_render(
        request, 
        'BotLaHug/club_pages/club_class_info.html', 
        context,
        club_name=club_name
    )

def generate_time_slots(classes, days_of_week):
    """
    Generates a dictionary of time slots for each day of the week based on the class schedule.

    Args:
        classes (QuerySet): A list of class objects containing the schedule.
        days_of_week (list): A list of days (Monday, Tuesday, etc.).

    Returns:
        dict: A dictionary where the keys are time slots and values are lists of classes per day.
    """
    from collections import defaultdict
    time_slots = defaultdict(lambda: {day: [] for day in days_of_week})

    for pk, class_info in classes.items():
        start_time = class_info['start_time']
        end_time = class_info['end_time']
        days = class_info['days']

     
        for day in days:
            day_name = dict(models.Class.DAYS_OF_WEEK)[day]
            time_slots[f'{start_time}-{end_time}'][day_name].append({
                'ID' : class_info['ID'],
                'name': class_info['name'],
                'teacher': class_info['teacher'],
                'time': f'{start_time} - {end_time}',
                'place': class_info['place'],
                'color': 'red',  # You can customize the color logic
            })

    return dict(time_slots)
