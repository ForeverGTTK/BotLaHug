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
    
    # more club views
    path('club/<str:club_name>/contact/', clubViews.contact, name='club_contact'),  
    
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
   
   # admin site
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
