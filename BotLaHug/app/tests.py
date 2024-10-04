from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import *


class ViewsTest(TestCase):
    def setUp(self):
        """
        Set up the initial data for testing the views.
        This method runs before every individual test.
        """
        self.user = User.objects.create(username="testuser")
        # Ensure Topics is properly imported and created
        self.topic = Topics.objects.create(name="Sports")
        
        self.club = Clubs.objects.create(
            name="Test Club",
            topic=self.topic,
            location="123 Test St",
            web_name="test-club",
            contact_email="test@example.com",
            contact_phone="1234567890",
            contact_person="John Doe"
        )
        
        # Create an article for the test
        self.article = Article.objects.create(
            title="Test Article",
            content="This is a test article",
            author=self.user,
            club=self.club,
            published=True
        )

        # Create an athlete for the test
        self.athlete = Athlete.objects.create(
            first_name="Test",
            last_name="Athlete",
            dob="2000-01-01",
            club=self.club,
            email="athlete@example.com",
        )
        
        # Create a feature for the test
        self.feature = Features.objects.create(
            club_ID=self.club,
            title="Test Feature",
            address="123 Feature St",
            price=500
        )
        
        self.image = Images.objects.create(
            club=self.club,
            page="home",
            name="logo",
            image="path_to_test_image.jpg" 
            )

    def test_home_view(self):
        """
        Test the home view for a specific club. Ensure that the page is rendered with the correct template and context.
        """
        response = self.client.get(reverse('club_home', kwargs={'club_name': self.club.web_name}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'BotLaHug/client_pages/club_home.html')
        self.assertIn('details', response.context)
        self.assertIn('articles', response.context)
        self.assertIn('schedule_classes', response.context)

    def test_contact_view(self):
        """
        Test the contact view to ensure it renders correctly and contains club details in the context.
        """
        response = self.client.get(reverse('club_contact', kwargs={'club_name': self.club.web_name}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'BotLaHug/client_pages/contact.html')
        self.assertIn('name', response.context)
        self.assertEqual(response.context['name'], 'test-club')

    def test_article_view(self):
        """
        Test the article view to ensure that the correct article is rendered with related articles.
        """
        response = self.client.get(reverse('article_detail', kwargs={
            'club_name': self.club.web_name,
            'article_ID': self.article.ID
        }))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'BotLaHug/client_pages/article.html')
        self.assertIn('article_details', response.context)
        self.assertEqual(response.context['article_details']['ID'], str(self.article.ID))

    def test_athlete_profile_view(self):
        """
        Test the athlete profile view to ensure the correct athlete is rendered.
        """
        response = self.client.get(reverse('athlete_profile', kwargs={
            'club_name': self.club.web_name,
            'athlete_id': self.athlete.ID
        }))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'BotLaHug/club_pages/athlete_profile.html')
        self.assertIn('athlete', response.context)
        self.assertEqual(response.context['athlete'].first_name, 'Test')

    def test_club_athletes_view(self):
        """
        Test the club athletes view to ensure the correct list of athletes is displayed.
        """
        response = self.client.get(reverse('club_athletes', kwargs={'club_name': self.club.web_name}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'BotLaHug/club_pages/club_athletes.html')
        self.assertIn('athletes', response.context)
        self.assertIn(self.athlete, response.context['athletes'])

    def test_find_athlete_view(self):
        """
        Test the find athlete view. Submit a search request and ensure that the correct athlete is found.
        """
        athlete = Athlete.objects.create(athlete_id="12345", club=self.club, first_name="John", last_name="Doe", dob="2000-01-01")
        response = self.client.get(reverse('find_athlete', kwargs={'club_name': self.club.web_name}), {
            'athlete_id': athlete.athlete_id  # Pass a valid athlete ID
        })
        self.assertEqual(response.status_code, 302)  # Redirect to athlete profile if found

    def test_club_classes_view(self):
        """
        Test the club classes view to ensure the list of classes for the current season is displayed.
        """
        response = self.client.get(reverse('club_classes', kwargs={'club_name': self.club.web_name}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'BotLaHug/club_pages/club_classes.html')
        self.assertIn('classes', response.context)

class ClubsModelTest(TestCase):
    def setUp(self):
        """
        Set up the initial data for testing the Clubs model, including topic relations.
        This method runs before every individual test.
        """
        self.user = User.objects.create(username="testuser")
        self.topic = Topics.objects.create(name="Sports")
        self.club = Clubs.objects.create(
            name="Test Club",
            topic=self.topic,
            location="123 Test St",
            web_name="test-club",
            contact_email="test@example.com",
            contact_phone="1234567890",
            contact_person="John Doe"
        )
        
        # Create a topic relation
        self.topic_relation = topic_relations.objects.create(
            topic=self.topic,
            club_ID=self.club
        )

    def test_club_creation(self):
        """
        Test if the Club instance is created successfully.
        """
        self.assertEqual(self.club.name, "Test Club")
        self.assertEqual(self.club.contact_email, "test@example.com")
        self.assertEqual(self.club.topic.name, "Sports")

    def test_get_club(self):
        """
        Test the get_club method for the Clubs model.
        """
        club_details = self.club.get_club()
        self.assertEqual(club_details['name'], "Test Club")
        self.assertEqual(club_details['location'], "123 Test St")

class FeaturesModelTest(TestCase):
    def setUp(self):
        """
        Set up initial data for testing the Features model, including topic relations.
        """
        self.user = User.objects.create(username="featureuser")
        self.topic = Topics.objects.create(name="Music")
        self.club = Clubs.objects.create(
            name="Music Club",
            topic=self.topic,
            location="456 Music Ave",
            web_name="music-club",
            contact_email="music@example.com",
            contact_phone="0987654321",
            contact_person="Jane Smith"
        )
        
        # Create a topic relation
        self.topic_relation = topic_relations.objects.create(
            topic=self.topic,
            club_ID=self.club
        )

        # Create a feature
        self.feature = Features.objects.create(
            club_ID=self.club,
            title="Recording Studio",
            address="Building A, Room 2",
            price=500
        )

    def test_feature_creation(self):
        """
        Test if the Feature instance is created successfully.
        """
        self.assertEqual(self.feature.title, "Recording Studio")
        self.assertEqual(self.feature.price, 500)
        self.assertEqual(self.feature.address, "Building A, Room 2")

    def test_get_club_fields(self):
        """
        Test the get_club_fields method of the Features model.
        """
        fields = self.feature.get_club_fields()
        self.assertEqual(fields['title'], "Recording Studio")
        self.assertEqual(fields['address'], "Building A, Room 2")
        self.assertNotIn('price', fields)
