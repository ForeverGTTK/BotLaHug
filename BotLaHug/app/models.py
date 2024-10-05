from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from multiselectfield import MultiSelectField
from django.utils import timezone
import uuid

class BaseModel(models.Model):
    """
    Base model providing common fields for all models.
    
    Fields:
        ID (UUIDField): Unique identifier, auto-generated.
        created_by (ForeignKey): The user who created the record.
        created_at (DateTimeField): Timestamp when the record was created, auto-generated.
        last_updated (DateTimeField): Timestamp when the record was last updated, auto-updated.
        description (TextField): Optional description field.
    """
    ID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

class Images(BaseModel):
    """
    Model representing images for clubs.

    Fields:
        image (ImageField): The image file.
        club (ForeignKey): Reference to the related club.
        page (CharField): Page or section where the image is used (e.g., 'Home', 'Article').
        name (CharField): Optional name for the image.
    """
    image = models.ImageField(upload_to='images/', null=False, blank=False)
    club = models.ForeignKey('Clubs', on_delete=models.CASCADE, related_name='images')
    page = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True, blank=True)

    def get_images_for_page(club, page: str, name: str = None) -> list:
        """
        Fetches images related to a specific club and page.

        Args:
            club (Clubs): The related club.
            page (str): The page the image is related to.
            name (str): Optional name filter.

        Returns:
            list: List of image URLs or descriptions.
        """
        if name is None:
            images = Images.objects.filter(club=club, page=page)
        else:
            images = Images.objects.filter(club=club, page=page, name=name)
        
        image_list = [image.image.url if image.image else "No image available" for image in images]
        return image_list

    def __str__(self):
        return f"Image for {self.club.name} on {self.page} page"

class Topics(BaseModel):
    """
    Model representing topics associated with clubs.
    
    Fields:
        name (TextField): The name of the topic, must be unique.
    """
    name = models.TextField(null=True, blank=True, unique=True)

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name

class Clubs(BaseModel):
    """
    Model representing clubs with attributes.
    
    Fields:
        name (CharField): The name of the club.
        topic (ForeignKey): The topic associated with the club.
        location (CharField): The location of the club.
        web_name (CharField): URL-friendly name of the club.
        contact_email (EmailField): Contact email for the club.
        contact_phone (CharField): Contact phone number for the club.
        contact_person (CharField): The main contact person for the club.
    """
    name = models.CharField(max_length=255, unique=True)
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE, null=True, related_name='clubs')
    location = models.CharField(max_length=255, null=True, blank=True)
    web_name = models.CharField(max_length=100, unique=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)
    contact_person = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        permissions = [
            ("view_club", "Can view club details"),
            ("manage_club", "Can manage club details"),
            ("manage_club_design", "Can edit club design"),
            ("manage_club_articles", "Can manage articles for the club"),
        ]
        
    def get_clubs_by_topic():
        """
        Returns a dictionary where the key is the club name and the value is a dictionary containing the photo URL, description, and web_name of each club associated with this topic.
        """
        # Fetch all clubs associated with this topic using topic_relations
        topics = Topics.objects.all()
        sorted_clubs = {}
        for topic in topics:
            club_relations = topic_relations.objects.filter(topic=topic)
            clubs = {}
            for relation in club_relations:
                club = relation.club_ID  # Access the club from the relation
            
               # Fetch images from the Images table
                image = get_object_or_404(Images,club=club, page='home',name='logo')

                # Create a dictionary with image URL, description, and web_name for each club
                clubs[club.name] = {
                    'photo': image,  # Get the first image URL if available
                    'description': club.description,
                    'web_name': club.web_name
                }
            sorted_clubs[topic.name] = {
                'club':clubs,
                'description':topic.description,
                }
        return sorted_clubs

    def get_club(self):
        """
        Returns a dictionary containing detailed club information, including related image.

        Returns:
            dict: Club information including name, contact details, and image.
        """
        image = get_object_or_404(Images, club=self.ID, page='home', name='logo')
        return {
            'ID': str(self.ID),
            'name': self.name,
            'location': self.location,
            'photo': image.image,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'contact_person': self.contact_person,
        }

    def __str__(self):
        return f'{self.name} - {self.topic.name if self.topic else "No Topic"}'

class topic_relations(BaseModel):
    """
    Model representing the many-to-many relationship between clubs and topics.

    Fields:
        topic (ForeignKey): Reference to the topic.
        club_ID (ForeignKey): Reference to the club.
    """
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE)
    club_ID = models.ForeignKey(Clubs, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.club_ID.name} related to {self.topic.name}'

class Design(BaseModel):
    """
    Model representing design attributes for a club's webpage.

    Fields:
        club (OneToOneField): Reference to the related club.
        color (CharField): Primary color of the webpage (hex format).
        text (TextField): Text content or style.
        font (CharField): Font style used on the webpage.
        background_image (ImageField): Background image for the webpage.
    """
    club = models.OneToOneField(Clubs, on_delete=models.CASCADE, related_name='design')
    color = models.CharField(max_length=7, default='#FFFFFF')  # Hex color
    text = models.TextField(null=True, blank=True)
    font = models.CharField(max_length=100, null=True, blank=True)
    background_image = models.ImageField(upload_to='design_backgrounds/', null=True, blank=True)

    def edit_design(self, new_color=None, new_text=None, new_font=None, new_background_image=None):
        """
        Updates the design attributes for a club's webpage.
        
        Args:
            new_color (str): Hex code for the new color.
            new_text (str): New text content.
            new_font (str): New font style.
            new_background_image (ImageField): New background image.
        """
        if new_color:
            self.color = new_color
        if new_text:
            self.text = new_text
        if new_font:
            self.font = new_font
        if new_background_image:
            self.background_image = new_background_image
        self.save()

    def __str__(self):
        return f"Design for {self.club.name}"

class Article(BaseModel):
    """
    Model representing articles in the system.

    Fields:
        title (CharField): The title of the article.
        content (TextField): Body of the article.
        author (ForeignKey): Reference to the user who created the article.
        club (ForeignKey): Reference to the related club.
        published (BooleanField): Status of the article (published or not).
        publication_date (DateTimeField): Date and time the article was published.
        tags (CharField): Optional tags related to the article.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    club = models.ForeignKey('Clubs', on_delete=models.CASCADE, related_name='articles')
    published = models.BooleanField(default=False)
    publication_date = models.DateTimeField(null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-publication_date']

    def __str__(self):
        return self.title

class Season(BaseModel):
    """
    Model representing a season for a club.

    Fields:
        club (ForeignKey): Reference to the related club.
        start_date (DateField): Start date of the season.
        end_date (DateField): End date of the season.
        is_active (BooleanField): Whether the season is currently active.
    """
    club = models.ForeignKey('Clubs', on_delete=models.CASCADE, related_name='seasons')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.club.name} Season {self.start_date.year} - {self.end_date.year}"

    def is_current_season(self):
        """
        Checks if the current date falls within the season's date range.

        Returns:
            bool: True if the season is current, False otherwise.
        """
        now = timezone.now().date()
        return self.start_date <= now <= self.end_date

class Athlete(BaseModel):
    """
    Model representing an athlete associated with a club.

    Fields:
        athlete_id (CharField): Unique identifier for the athlete.
        club (ForeignKey): Reference to the related club.
        first_name (CharField): Athlete's first name.
        last_name (CharField): Athlete's last name.
        dob (DateField): Date of birth of the athlete.
        email (EmailField): Athlete's email address.
        phone (CharField): Athlete's phone number.
        parent_name (CharField): Athlete's parent or guardian's name.
        parent_phone (CharField): Phone number of the parent or guardian.
        home_address (TextField): Home address of the athlete.
        profile_picture (ImageField): Profile picture of the athlete.
    """
    athlete_id = models.CharField(max_length=10, null=True, blank=True)
    club = models.ForeignKey('Clubs', on_delete=models.CASCADE, related_name='athletes')
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    dob = models.DateField(null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    phone = models.CharField(max_length=10, null=False, blank=True)
    parent_name = models.CharField(max_length=100, null=True, blank=True)
    parent_phone = models.CharField(max_length=10, null=True, blank=True)
    home_address = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def get_athlete(self):
        """
        Returns a dictionary of the athlete's details.

        Returns:
            dict: Athlete details including name, contact information, and profile picture.
        """
        return {
            'ID': self.ID,
            'athlete_id': self.athlete_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'dob': self.dob,
            'email': self.email,
            'phone': self.phone,
            'parent_name': self.parent_name,
            'parent_phone': self.parent_phone,
            'home_address': self.home_address,
            'profile_picture': self.profile_picture.url if self.profile_picture else None,
        }

    def __str__(self):
        return f'{self.first_name} {self.last_name} (Athlete ID: {self.athlete_id})'

class Class(BaseModel):
    """
    Model representing a class within a season for a club.

    Fields:
        name (CharField): Name of the class.
        season (ForeignKey): Reference to the season the class belongs to.
        start_date (DateField): Start date of the class.
        end_date (DateField): End date of the class.
        days_of_week (MultiSelectField): Days of the week when the class is held.
        start_time (TimeField): Start time of the class.
        end_time (TimeField): End time of the class.
        place (CharField): Location of the class.
        teacher (ForeignKey): Reference to the class instructor.
        price (DecimalField): Price of the class.
        registration_fee (DecimalField): Registration fee for the class.
    """
    DAYS_OF_WEEK = (
        ('sun', 'Sunday'),
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
    )
    
    name = models.CharField(max_length=255)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='classes')
    start_date = models.DateField()
    end_date = models.DateField()
    days_of_week = MultiSelectField(choices=DAYS_OF_WEEK, null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    place = models.CharField(max_length=255, null=True, blank=True)
    #teacher = models.CharField(max_length=255, null=True, blank=True)

    teacher = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['start_date', 'start_time']

    def __str__(self):
        return f"{self.name} - {self.season}"

    @classmethod
    def get_classes_by_current_season(cls, club):
        """
        Fetches the classes related to the current season for a specific club.

        Args:
            club (Clubs): The club for which to fetch classes.

        Returns:
            dict: A dictionary of class details including name, schedule, and instructor.
        """
        current_season = Season.objects.filter(club=club, is_active=True).first()
        if not current_season:
            return {}
        
        classes = cls.objects.filter(season=current_season)
        return {
            c.name: {
                'ID': c.ID,
                'name': c.name,
                'teacher': c.teacher,
                'place': c.place,
                'price': c.price,
                'registration_fee': c.registration_fee,
                'start_time': c.start_time.strftime('%H:%M'),
                'end_time': c.end_time.strftime('%H:%M'),
                'days': c.days_of_week,
            }
            for c in classes
        }

class Features(BaseModel):
    """
    Model representing additional features offered by a club.

    Fields:
        club_ID (ForeignKey): Reference to the related club.
        title (CharField): Title or name of the feature.
        address (TextField): Location or relevant address for the feature.
        price (DecimalField): Price of the feature.
    """
    club_ID = models.ForeignKey('Clubs', on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=255)
    address = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-title']
        permissions = [
            ("view_class", "Can view class"),
            ("manage_class", "Can manage class details"),
            ("manage_registrations", "Can manage class registrations"),
            ("assign_teacher", "Can assign teacher to class"),
        ]


    def get_club_fields(self):
        """
        Retrieves a dictionary containing feature details, excluding price.

        Returns:
            dict: Feature details including club, title, and address.
        """
        return {
            'club_ID': str(self.club_ID),
            'title': self.title,
            'address': self.address,
        }

    def get_club_price(self):
        """
        Retrieves a dictionary including all feature details, including price.

        Returns:
            dict: Full feature details including price.
        """
        return {
            **self.get_club_fields(),
            'price': self.price,
        }

    def __str__(self):
        return f"{self.title} - {self.club_ID.name}"

class Registration(BaseModel):
    """
    Represents the registration of an athlete for a specific class.

    Fields:
        athlete (ForeignKey to Athlete): The athlete who is registering for the class.
        class_id (ForeignKey to Class): The class that the athlete is registering for.
        status (CharField): The status of the athlete in the class (e.g., 'active', 'inactive').
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    
    athlete = models.ForeignKey('Athlete', on_delete=models.CASCADE, related_name='registrations')
    class_id = models.ForeignKey('Class', on_delete=models.CASCADE, related_name='registrations')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    class Meta:
        ordering = ['-created_at']

    def get_class_athlete(self):
        """
        Retrieves detailed information about the athlete registered for a class.

        Returns:
            dict: A dictionary with the athlete's name, date of birth, year joined, and description.
        """
        return {
            'name': f'{self.athlete.first_name} {self.athlete.last_name}',
            'dob': self.athlete.dob.strftime('%Y-%m-%d'),
            'year_joined': self.created_at.year,
            'description': self.athlete.description if self.athlete.description else 'No description available',
        }

    def __str__(self):
        return f"{self.athlete.first_name} {self.athlete.last_name} registered for {self.class_id.name} - {self.status}"

class Teacher(BaseModel):
    """
    Model representing a teacher.
    
    Fields:
        first_name (CharField): First name of the teacher.
        last_name (CharField): Last name of the teacher.
        email (EmailField): Email address of the teacher.
        phone (CharField): Phone number of the teacher.
        biography (TextField): Short biography of the teacher.
        profile_image (ForeignKey): Link to the teacher's profile image in the Images model.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    profile_image = models.ForeignKey('Images', on_delete=models.SET_NULL, null=True, related_name='teacher_images')

    class Meta:
        permissions = [
            ("manage_teacher", "Can add, edit, or remove teachers"),
            ("assign_classes", "Can assign classes to teachers"),
        ]

    def get_teacher_info(self):
        """
        Returns a dictionary containing the teacher's details.
        """
        return {
            'name': f'{self.first_name} {self.last_name}',
            'email': self.email,
            'phone': self.phone,
            'biography': self.biography,
            'profile_image': self.profile_image.image.url if self.profile_image else None,
        }

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TeacherRelations(BaseModel):
    """
    Model representing the relationship between teachers and classes.
    
    Fields:
        teacher (ForeignKey): Reference to the teacher.
        class_id (ForeignKey): Reference to the class the teacher is associated with.
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_relations')
    class_id = models.ForeignKey('Class', on_delete=models.CASCADE, related_name='teacher_class_relations')
    tuval = models.CharField(max_length=100,null=True,blank = True)

    def __str__(self):
        return f"{self.teacher} teaches {self.class_id.name}"