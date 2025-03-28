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
        
        # Add fields for both Google and SSO UI authentication
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', 'guest')  # Default role
        
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
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('pengguna', 'Pengguna'),
        ('admin', 'Admin'),
        ('guest', 'Guest'),
    ]

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
    
    # Google OAuth fields
    google_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        unique=True,
        help_text='Google account identifier for OAuth authentication.'
    )
    
    # SSO UI fields
    npm = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True,
        help_text='Student ID number from SSO UI.'
    )
    
    angkatan = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        help_text='Student year (angkatan).'
    )
    
    noWA = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='WhatsApp number.'
    )
    
    # Common fields for both authentication methods
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='pengguna',
        help_text='User role in the application.'
    )
    
    # Redefine username field to ensure it's explicitly tied to email or SSO username
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Username for compatibility with Django. Defaults to email.',
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'