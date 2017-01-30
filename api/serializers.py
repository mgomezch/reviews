from rest_framework.serializers import HyperlinkedModelSerializer

from reviews.models import (
    Company,
    Review,
    Reviewer,
    User,
)


class UserSerializer(HyperlinkedModelSerializer):

    class Meta:

        model = User

        # Django's default User model has numerous fields used internally by the
        # authentication system but not relevant to this API; this exposes only
        # the few that may be useful here.
        fields = [
            'self',
            'created',
            'modified',
            'username',
            'email',
            'is_staff',
        ]

        # These fields are determined automatically and should be rejected in
        # object creation requests.
        read_only_fields = [
            'created',
            'modified',
        ]

        extra_kwargs = {
            'self': {
                # Users are looked up by username, not by their ID number.
                'lookup_field': 'username',
            },
        }


class CompanySerializer(HyperlinkedModelSerializer):

    class Meta:

        model = Company
        fields = '__all__'

        # These fields are determined automatically and should be rejected in
        # object creation requests.
        read_only_fields = [
            'created',
            'modified',
        ]


class ReviewerSerializer(HyperlinkedModelSerializer):

    class Meta:

        model = Reviewer

        fields = [
            'self',
            'created',
            'modified',
            'name',
            'email',  # Non-default primary keys have to be included explicitly
        ]

        # These fields are determined automatically and should be rejected in
        # object creation requests.
        read_only_fields = [
            'created',
            'modified',
        ]

        extra_kwargs = {
            'self': {
                # Reviewers are looked up by e-mail address; they have no
                # numeric ID.
                'lookup_field': 'email',
            },
        }


class ReviewSerializer(HyperlinkedModelSerializer):

    class Meta:

        model = Review
        fields = '__all__'

        # These fields are determined automatically and should be rejected in
        # object creation requests.
        read_only_fields = [
            'created',
            'modified',
            'ip_address',
            'submitter',
        ]

        extra_kwargs = {
            'reviewer': {
                # Reviewers are looked up by e-mail address; they have no
                # numeric ID.
                'lookup_field': 'email',
            },
            'submitter': {
                # Users are looked up by username, not by their ID number.
                'lookup_field': 'username',
            },
        }
