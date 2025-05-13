import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        
        Args:
            email: User's email address
            password: User's password (optional)
            **extra_fields: Additional fields for the user
            
        Returns:
            The newly created user
        
        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        
        email = self.normalize_email(email)
        
        if 'username' not in extra_fields:
            extra_fields['username'] = email.split('@')[0]
        
        # Set defaults for required fields
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', 'user')
        
        # Create the user
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        
        Args:
            email: User's email address
            password: User's password
            **extra_fields: Additional fields for the user
            
        Returns:
            The newly created superuser
            
        Raises:
            ValueError: If required superuser attributes are not True
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        extra_fields['username'] = email.split('@')[0]
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom user model with additional fields for Google OAuth and SSO UI authentication.
    """
    
    ROLE_CHOICES = [
        ('user', _('Regular User')),
        ('admin', _('Administrator')),
    ]
    
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_('Unique identifier for the user')
    )
    
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
        help_text=_('Required. The user\'s email address.')
    )
    
    # Google OAuth fields
    google_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        unique=True,
        help_text=_('Google account identifier for OAuth authentication.')
    )
    
    # SSO UI fields
    npm = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        unique=True,
        help_text=_('Student ID number from SSO UI.')
    )
    
    angkatan = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        help_text=_('Student year (angkatan).')
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        help_text=_('User role in the application.')
    )
    
    # Redefine username field to ensure it's explicitly tied to email or SSO username
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=_('Username for compatibility with Django. Defaults to email.'),
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="custom_user_groups",
        related_query_name="custom_user",
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_permissions",
        related_query_name="custom_user",
    )
    
    # Basic user settings
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['email']
    
    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email
    
    def get_short_name(self):
        return self.first_name if self.first_name else self.email.split('@')[0]
    
    def is_admin(self):
        return self.role == 'admin'
        
    def has_role(self, role):
        return self.role == role