from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, UserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    USERNAME_FIELD = 'email'

    ROLES = [
        ('admin', 'admin'),
        ('customer', 'customer'),
        ('collaborator', 'collaborator'),
    ]

    cpf = models.CharField('CPF', max_length=11, primary_key=True, unique=True)
    email = models.EmailField('email address', unique=True)
    full_name = models.CharField('full name', max_length=255)
    is_active = models.BooleanField('is active', default=True)
    is_staff = models.BooleanField('is staff', default=False)
    is_superuser = models.BooleanField('is superuser', default=False)
    role = models.CharField('user role', default='user', choices=ROLES, max_length=20)

    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
