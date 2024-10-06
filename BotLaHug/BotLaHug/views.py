"""
views of bot lahug application clubs views
"""


import os,re
from datetime import time, datetime, timedelta, date  
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, JsonResponse
from django.db.models import Count
from collections import defaultdict
from app import models
from app.forms import AthleteRegistrationForm, RegistrationForm,ExistingAthleteRegistrationForm,ClassForm,TeacherForm



def is_manager(user):
    return user.groups.filter(name='Manager').exists()

def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()

def is_client(user):
    return user.groups.filter(name='Client').exists()


# Manager-only view
@user_passes_test(is_manager)
@login_required
def manager_dashboard(request):
    # Manager-only functionality
    context = {
        'clubs': Clubs.objects.all(),
        'tasks': 'Manager specific tasks here'
    }
    return render(request, 'BotLaHug/manager_pages/dashboard.html', context)

# Teacher-only view
@user_passes_test(is_teacher)
@login_required
def teacher_classes(request, club_name):
    club = get_object_or_404(Clubs, web_name=club_name)
    classes = Class.objects.filter(teacher=request.user)
    
    return page_render(
        request, 
        'BotLaHug/teacher_pages/teacher_classes.html', 
        {'classes': classes},
        club_name=club_name
    )
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
            'image': image.image if image else None,
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

def athlete_profile(request, club_name, athlete_id):
    athlete = get_object_or_404(models.Athlete, ID=athlete_id)

    # Fetch the registration data
    registration_data = models.Registration.get_registration(athlete)

    context = {
        'athlete': athlete,
        'registration_data': registration_data,
    }

    return page_render(
        request, 
        'BotLaHug/club_pages/athlete_profile.html', 
        context,
        club_name=club_name
    )

@login_required
@user_passes_test(lambda user: is_manager(user) or is_teacher(user))
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
                'club_logo_url': club.get_club()['photo'],
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
        'club_logo_url': club.get_club()['photo'],
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
        'ID': class_instance.ID,
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
        days = class_info['days_of_week']

     
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

#------------------------------------------- Forms -------------------------------------------------

def register_athlete(request, club_name, class_id=None):
    club = get_object_or_404(models.Clubs, web_name=club_name)
    current_season = models.Season.objects.filter(club=club, is_active=True).first()
    class_instance = get_object_or_404(models.Class, season=current_season,ID = class_id)


    if request.method == 'POST':
        athlete_form = AthleteRegistrationForm(request.POST)
        registration_form = RegistrationForm(request.POST)

        if athlete_form.is_valid() and registration_form.is_valid():
            # Handle the athlete creation
            athlete = athlete_form.save(commit=False)
            athlete.created_by = request.user if request.user.is_authenticated else 'Guest'
            athlete.description = f'{club_name} athlete, joined the club in the {current_season} season, trains in {class_instance.name} class'
            athlete.club = club
            athlete.save()

            # Handle the registration creation
            registration = registration_form.save(commit=False)
            registration.created_by = request.user if request.user.is_authenticated else 'Guest'
            registration.description = 'Form auto created registration'
            registration.athlete = athlete
            registration.class_id = class_instance
            registration.status = 'New'
            registration.save()

            return redirect('athlete_profile', club_name=club_name , athlete_id = athlete.ID)

    else:
        athlete_form = AthleteRegistrationForm()
        registration_form = RegistrationForm()

    context = {
        'athlete_form': athlete_form,
        'registration_form': registration_form,
        'club_name': club_name,
        'club_logo': club.get_club().get('photo'),
    }

    return page_render(
        request, 
        'BotLaHug/client_pages/athlete_registration_form.html', 
        context,
        club_name=club_name
    )

def register_existing_athlete(request, club_name, athlete_id):
    club = get_object_or_404(models.Clubs, web_name=club_name)
    athlete = get_object_or_404(models.Athlete, athlete_id=athlete_id)

    if request.method == 'POST':
        form = ExistingAthleteRegistrationForm(request.POST, club=club)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.created_by = request.user if request.user.is_authenticated else 'Guest'
            registration.description = 'Form auto created registration'
            registration.athlete = athlete

            selected_class = form.cleaned_data['classes']
            registration.class_id = selected_class

            class_details = selected_class.get_class()
            registration.status = 'New'
            registration.save()

            return redirect('athlete_profile', club_name=club_name, athlete_id=athlete.ID)
    else:
        form = ExistingAthleteRegistrationForm(club=club)
    context = {
        'form': form,
        'club_name': club_name,
        'club_logo': club.get_club().get('photo'),
    }

    return page_render(
        request, 
        'BotLaHug/client_pages/class_registration_form.html', 
        context,
        club_name=club_name
    )


@login_required
@user_passes_test(is_manager)
def edit_class(request,club_name, class_id):
    """
    Handles adding or editing a class for manager users.

    Args:
        request: HttpRequest object
        class_id: Optional, if provided the form will edit an existing class.

    Returns:
        Rendered form for creating or updating a class.
    """
    if class_id:
        class_instance = get_object_or_404(models.Class, ID=class_id)
    else:
        class_instance = None
    club_logo = get_object_or_404(models.Clubs, web_name=club_name).get_club()['photo']

    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_instance)
        if form.is_valid():
            class_obj = form.save(commit=False)
            class_obj.created_by = request.user  # Set the current user as creator
            class_obj.save()
            return redirect('club_classes',club_name= club_name)  # Redirect to a class list page or another relevant page
    else:
        form = ClassForm(instance=class_instance)

    context = {
        'form': form,
        'is_editing': class_instance is not None,
        'club_logo_url': club_logo,
    }
    return page_render(request, 'BotLaHug/manager_pages/class_form.html', context,        club_name=club_name
 )

def manage_class(request,club_name):
    
    return edit_class(request, club_name=club_name,class_id=None)


def schedule_view(request, club_name):
    """
    Renders the club schedule page with the weekly class schedule.

    Args:
        request (HttpRequest): The HTTP request object.
        club_name (str): The web_name of the club used to retrieve the specific club instance.

    Returns:
        HttpResponse: Rendered club schedule page with class times.
    """
    club = get_object_or_404(models.Clubs, web_name=club_name)
    classes = models.Class.get_classes_by_current_season(club=club)
    days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    schedule_classes = generate_time_slots(classes, days_of_week)

    return page_render(
        request,
        'BotLaHug/client_pages/schedule.html',
        {
            'schedule_classes': schedule_classes,
            'days_of_week': days_of_week,
            'club_name': club_name,
            'club_logo_url': club.get_club().get('photo'),
        },
        club_name=club_name
    )

def teacher_view(request, club_name, teacher_id):
    """
    Renders the teacher's page displaying the classes they teach.

    Args:
        request (HttpRequest): The HTTP request object.
        club_name (str): The web_name of the club.
        teacher_id (int): The ID of the teacher.

    Returns:
        HttpResponse: Rendered teacher page with the classes they teach.
    """
    club = get_object_or_404(models.Clubs, web_name=club_name)
    teacher = get_object_or_404(models.Teacher, ID=teacher_id)
    classes = models.Class.objects.filter(teacher=teacher, season=models.Season.objects.filter(club=club, is_active=True).first())

    classes_dict = {
        class_obj.name: class_obj for class_obj in classes
    }

    return page_render(
        request,
        'BotLaHug/club_pages/teacher_classes.html',
        {
            'name': teacher.get_full_name(),
            'classes': classes_dict,
            'club_name': club_name
        },
        club_name=club_name
    )

def add_teacher(request, club_name):
    """
    View to add a new teacher to the club, with teacher-specific permissions.

    Args:
        request (HttpRequest): The HTTP request object.
        club_name (str): The web_name of the club.

    Returns:
        HttpResponse: Rendered teacher form page, or redirect after success.
    """
    club = get_object_or_404(models.Clubs, web_name=club_name)

    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            # Create the user with the provided data
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Assign teacher permissions (add the user to the teacher group)
            teacher_group, created = Group.objects.get_or_create(name='Teacher')
            user.groups.add(teacher_group)

            # Create the Teacher instance (assuming there is a Teacher model)
            models.Teacher.objects.create(user=user, club=club, **form.cleaned_data)

            return redirect('teacher_view', club_name=club_name, teacher_id=user.id)

    else:
        form = TeacherForm()

    return render(request, 'BotLaHug/manager_pages/teacher_form.html', {'form': form, 'club_name': club_name})

def connected_teachers(request, club_name):
    """
    Renders the connected teachers for the given club.
    
    Args:
        request (HttpRequest): The HTTP request object.
        club_name (str): The name of the club to fetch teachers for.

    Returns:
        HttpResponse: Rendered page displaying the teachers.
    """
    club = get_object_or_404(models.Clubs, web_name=club_name)
    
    # Assuming you have a way to identify teachers in your system
    teachers = models.User.objects.filter(groups__name='Teachers')  # Assuming you have a 'Teachers' group
    
    context = {
        'name': club_name,
        'teachers': teachers,
    }
    
    return render(request, 'BotLaHug/manager_pages/club_teacher.html', context)
