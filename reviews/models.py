from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    EmailField,
    ForeignKey,
    GenericIPAddressField,
    IntegerField,
    PROTECT,
    TextField,
    URLField,
)

from model_utils.models import TimeStampedModel
from rest_framework.authtoken.models import Token


# All our models will inherit creation and modification time tracking from this
# abstract base model class, as well as ordering based on creation timestamp.
class Model(TimeStampedModel):

    class Meta:
        abstract = True
        get_latest_by = 'created'


# This is not redundant.  It's best to have a separate User model from the start
# of a project to avoid later complications if it ever becomes necessary to add
# extra fields or change the definition of existing fields in the User model.
# See https://code.djangoproject.com/ticket/25313
class User(AbstractUser, Model):
    '''
    Users of this review tracking system.  Users may log into the system and \
    publish reviews of any company authored by any reviewer.  Users may also \
    manage company and reviewer registration in the system's database.
    '''

    def __str__(self):
        return self.username


# Create authentication tokens for users automatically after saving new Users:
@receiver(
    post_save,
    sender=User,
)
def create_auth_token(
    sender,
    instance=None,
    created=False,
    **kwargs
):
    if created:
        Token.objects.create(
            user=instance,
        )


class Company(Model):
    '''
    Companies that may be the object of reviews tracked by this system.  \
    Companies may be registered by any user.  Reviews may be submitted for any \
    registered company by any user.
    '''

    name = CharField(
        max_length=64,
        help_text='Name of the company; e.g. ACME, Inc.',
    )

    url = URLField(
        blank=True,
        help_text='Address of the company website; e.g. http://example.com/',
    )

    class Meta:
        verbose_name_plural = 'companies'

    def __str__(self):
        return f'{self.name} ({self.pk})'


class Reviewer(Model):
    '''
    Reviewers who may author reviews tracked by this system.  Reviewers may be \
    registered by any user.  Reviews may be submitted by users on behalf of \
    any registered reviewer.
    '''

    email = EmailField(
        primary_key=True,
        help_text='E-mail address of the reviewer; e.g. john.doe@example.com',
    )

    name = CharField(
        max_length=256,
        blank=True,
        help_text='Name of the reviewer; e.g. John Doe',
    )

    def __str__(self):
        return f'{self.name} ({self.email})'


class Review(Model):
    '''
    Reviews tracked by this system.  Each review specifies the company being \
    reviewed and the review author.  Reviews may be submitted by any user for \
    any registered company and reviewer.  Non-admin users can only see and \
    interact with reviews they submitted themselves.
    '''

    submitter = ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        help_text='User that submitted the review into this system',
    )

    rating = IntegerField(
        choices=[
            (x, str(x))
            for x in range(1, 6)
        ],
        help_text='Numeric rating between 1 (worst) and 5 (best); e.g. 4',
    )

    title = CharField(
        max_length=64,
        blank=True,
        help_text='Review title; e.g. Awesome company!',
    )

    summary_max_length = 10000
    summary = TextField(
        max_length=summary_max_length,
        blank=True,
        help_text=(
            f'Summary of up to {summary_max_length} characters recounting the '
            'reviewer\'s experience with the company under review'
        ),
    )

    ip_address = GenericIPAddressField(
        help_text='Internet network address that provided this review',
    )

    company = ForeignKey(
        to=Company,
        on_delete=PROTECT,
        help_text='Company to whom this review applies',
    )

    reviewer = ForeignKey(
        to=Reviewer,
        on_delete=PROTECT,
        help_text='Reviewer who authored this review',
    )

    def __str__(self):
        return f'{self.title} ({self.pk})'
