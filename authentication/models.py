import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['email']

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')

        email = self.normalize_email(email)
        
        if 'username' not in extra_fields:
            extra_fields['username'] = email
            
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='Unique identifier for the user'
    )

    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': "A user with that email already exists.",
        },
        help_text='Required. The user\'s email address.'
    )
    
    google_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        unique=True,
        help_text='Google account identifier for OAuth authentication.'
    )
    
    # Redefine username field to ensure it's explicitly tied to email
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Username for compatibility with Django. Defaults to email.',
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )

    given_name = models.CharField(
        max_length=30, 
        blank=True, 
        help_text='User\'s given name (first name).'
    )
    family_name = models.CharField(
        max_length=30, 
        blank=True, 
        help_text='User\'s family name (last name).'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        full_name = f"{self.given_name} {self.family_name}".strip()
        
        return full_name or self.email