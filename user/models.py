from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import ImageField
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from django.db.models.signals import pre_save
import os
from django.dispatch import receiver

def get_avatar_path(instance, filename):
    # get the file extension
    ext = filename.split('.')[-1]
    filename = f"{instance.username}.{ext}"
    # return the upload path with the username and the extension
    return f"users/avatar/{filename}"

class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_("email address"), blank=False, null=False)
    nickname= models.CharField(_("nick name"), max_length=150, blank=True)
    phone_number= models.CharField(_('phone number'), blank=True, max_length=11)
    avatar = ImageField(upload_to=get_avatar_path, blank=True)
    bio=models.TextField(_("bio"), blank=True)
    website= models.URLField(_("website"), blank=True)
    is_varified= models.BooleanField(_("is varified"), default=False)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if self.avatar:
            im = Image.open(self.avatar)
            im.thumbnail((300, 300), Image.LANCZOS)
            width, height = im.size   # Get dimensions
            new_size = 200

            left = (width - new_size) // 2
            top = (height - new_size) // 2
            right = (width + new_size) // 2
            bottom = (height + new_size) // 2

            # Crop the center of the image
            im = im.crop((left, top, right, bottom))


            output = BytesIO()
            im.save(output, format='JPEG', subsampling=0, quality=95)
            output.seek(0)

            # change the imagefield value to be the newly modified image value
            self.avatar = InMemoryUploadedFile(output, 'ImageField',
                                                    "%s.jpg" % self.avatar.name.split('.')[0], 'image/jpeg',
                                                    sys.getsizeof(output), None)
            
        try:
            this = User.objects.get(id=self.id)
            if this.avatar != self.avatar:
                this.avatar.delete()
        except: pass
        super(User, self).save()

