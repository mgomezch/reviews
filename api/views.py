from api.serializers import (
    CompanySerializer,
    ReviewSerializer,
    ReviewerSerializer,
    UserSerializer,
)

from ipware.ip import get_ip

from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from reviews.models import (
    Company,
    Review,
    Reviewer,
    User,
)


class UserViewSet(ReadOnlyModelViewSet):
    # TODO: implement user creation and the like

    serializer_class = UserSerializer
    __doc__ = serializer_class.Meta.model.__doc__

    lookup_field = 'username'
    queryset = User.objects.all()


class CompanyViewSet(ModelViewSet):

    serializer_class = CompanySerializer
    __doc__ = serializer_class.Meta.model.__doc__

    queryset = Company.objects.all()


class ReviewerViewSet(ModelViewSet):

    serializer_class = ReviewerSerializer
    __doc__ = serializer_class.Meta.model.__doc__

    queryset = Reviewer.objects.all()

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
    # TODO: permissions; users can still see and edit reviews they don't own

    serializer_class = ReviewSerializer
    __doc__ = serializer_class.Meta.model.__doc__

    queryset = Review.objects.all()

    # Override the default queryset so that regular, non-admin users can only
    # see reviews they submitted themselves; only admin users see every review.
    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user
        return (
            queryset
            if user.is_staff
            else user.reviews
        ).all()

    # Customize new review submission:
    def perform_create(self, serializer):
        serializer.save(

            # Get the IP address from request headers; see
            # https://github.com/un33k/django-ipware
            ip_address=get_ip(self.request),

            # Auto-assign review submitter from the submission request user:
            submitter=self.request.user,

        )
