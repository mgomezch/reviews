from api.filters import (
    ReviewFilterBackend,
    UserFilterBackend,
)

from api.serializers import (
    CompanySerializer,
    ReviewSerializer,
    ReviewerSerializer,
    UserSerializer,
)

from dry_rest_permissions.generics import DRYPermissions, DRYObjectPermissions
from ipware.ip import get_ip

from rest_framework.viewsets import ModelViewSet

from reviews.models import (
    Company,
    Review,
    Reviewer,
    User,
)


class UserViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    __doc__ = serializer_class.Meta.model.__doc__

    filter_backends = (UserFilterBackend, )
    permission_classes = (DRYPermissions, )

    # The API identifies users by usernames instead of the default numeric
    # primary key, so the lookup_field attribute must be specified explicitly:
    lookup_field = 'username'


class CompanyViewSet(ModelViewSet):

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    __doc__ = serializer_class.Meta.model.__doc__


class ReviewerViewSet(ModelViewSet):

    queryset = Reviewer.objects.all()
    serializer_class = ReviewerSerializer
    __doc__ = serializer_class.Meta.model.__doc__

    # The Reviewer model has a non-default primary key, so the lookup_field
    # attribute must be specified explicitly:
    lookup_field = 'email'

    # The Reviewer model's lookup field can contain dots (e-mail addresses often
    # do!), and the default regular expression used to match lookup field values
    # in URLs assumes dots are not part of the lookup field value.  This allows
    # any character other than / or ? to occur within the reviewer's e-mail
    # address.  A more strict specification of e-mail address syntax is of
    # course possible with a regular expression, but it's generally not thought
    # to be a good idea: http://www.ex-parrot.com/pdw/Mail-RFC822-Address.html
    lookup_value_regex = '[^/?]+'


class ReviewViewSet(ModelViewSet):

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    __doc__ = serializer_class.Meta.model.__doc__

    filter_backends = (ReviewFilterBackend, )
    permission_classes = (DRYObjectPermissions, )

    # Customize new review submission:
    def perform_create(self, serializer):
        serializer.save(

            # Get the IP address from request headers; see
            # https://github.com/un33k/django-ipware
            ip_address=get_ip(self.request),

            # Auto-assign review submitter from the submission request user:
            submitter=self.request.user,

        )
