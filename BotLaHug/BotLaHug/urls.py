"""
Definition of urls for BotLaHug.
"""

from datetime import datetime
from django.urls import include, path
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls.static import static
from app import forms as btlforms
from app import views as btlviews
from BotLaHug import views as clubViews
from schema_graph.views import Schema

urlpatterns = [
    # club views    
    path('club/<str:club_name>/', clubViews.home, name='club_home'), 
    path('club/<str:club_name>/articles/<str:article_ID>', clubViews.article, name='article_detail'), 
    
    # athlete club views
    path('club/<str:club_name>/athlete/<str:athlete_id>', clubViews.athlete_profile, name='athlete_profile'),  
    path('club/<str:club_name>/athlete/', clubViews.find_athlete, name='find_athlete'),
    path('club/<str:club_name>/athletes/', clubViews.club_athletes, name='club_athletes'),
    
    # classes club views
    path('club/<str:club_name>/classes/', clubViews.club_classes, name='club_classes'),  
    path('club/<str:club_name>/class/<str:class_id>', clubViews.class_info, name='class_info'),
    path('club/<str:club_name>/class/register/<str:class_id>', clubViews.register_athlete, name='register_athlete'),
    path('club/<str:club_name>/class/athlete/register/<str:athlete_id>', clubViews.register_existing_athlete, name='register_existing_athlete'),  

    path('club/<str:club_name>/class/view/<str:class_id>', clubViews.club_class_info, name='club_class_info'),

    path('club/<str:club_name>/manage/newClass/', clubViews.manage_class, name='add_class'),
    path('/club/<str:club_name>/manage/class/<str:class_id>', clubViews.edit_class, name='edit_class'),

    # more club details
    path('club/<str:club_name>/contact/', clubViews.contact, name='club_contact'),
    path('club/<str:club_name>/about/', clubViews.about, name='club_about'),  

    path('club/<str:club_name>/schedule/', clubViews.schedule_view, name='club_schedule'),

    path('club/<str:club_name>/teacher/<int:teacher_id>/', clubViews.teacher_view, name='teacher_view'),
    path('club/<str:club_name>/teacher/add/', clubViews.add_teacher, name='add_teacher'),
    path('club/<str:club_name>/teachers/', clubViews.connected_teachers, name='connected_teachers'),

    # app views from btl - bot_La_hug
    path('', btlviews.home, name='home'), 
    path('contact/', btlviews.contact, name='contact'), 
    path('about/', btlviews.about, name='about'), 
    
    # login/logout views
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=btlforms.BootstrapAuthenticationForm,
             extra_context={
                 'title': 'Log in',
                 'year': datetime.now().year,
             }
         ),
         name='login'), 
    path('logout/', LogoutView.as_view(next_page=''), name='logout'), 
    path("schema/", Schema.as_view()),  

   # admin site
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
