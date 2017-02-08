from api.strategies import (
    emails,
    passwords,
    usernames,
)

from api.testcase import GabbiHypothesisTestCase
from api.utils.database import delete_all
from django.db.transaction import commit
from django.urls import reverse

from hypothesis import (
    Verbosity,
    assume,
    given,
    settings,
)

from hypothesis.strategies import booleans
from requests.auth import _basic_auth_str
from rest_framework.authtoken.models import Token
from reviews.models import User


class UserTestSuite(GabbiHypothesisTestCase):
    fixtures = [
        'test_admin',
        'test_nonadmin',
    ]

    version = 'v1'

    # For performance, disable truncation of the entire database and clear only
    # modified tables here:
    def _fixture_teardown(self):
        delete_all(Token)
        delete_all(User)

    @given(
        username=usernames,
        password=passwords,
        email=emails,
        is_staff=booleans(),
    )
    @settings(
        perform_health_check=False,  # FIXME
        verbosity=Verbosity.verbose,
    )
    def test_create_user(
        self,
        username,
        password,
        email,
        is_staff,
    ):

        admin_username = 'test_admin'
        admin_password = 'xyzzy'

        nonadmin_username = 'test_nonadmin'
        nonadmin_password = 'xyzzy'

        assume(admin_username != username)
        assume(nonadmin_username != username)

        # For a yet unknown reason, using a single dot as a username breaks this
        # test: it seems the Django request parser discards the dot at the end
        # of request URIs for /v1/user/. and this makes the request fail in the
        # URL resolver.  This skips such tests:
        assume(username != '.')

        admin_auth_string = _basic_auth_str(
            username=admin_username,
            password=admin_password,
        )

        nonadmin_auth_string = _basic_auth_str(
            username=nonadmin_username,
            password=nonadmin_password,
        )

        new_user_auth_string = _basic_auth_str(
            username=username,
            password=password,
        )

        # This ensures the admin user provided by fixtures is actually available
        # to other requests:
        commit()

        self.run_gabbi(
            {
                'tests': [

                    # Test failure on attempt to create a new user as a
                    # non-administrator user:
                    {
                        'name': 'fail create new user as nonadmin',
                        'url': reverse(self.version + ':user-list'),
                        'method': 'POST',
                        'request_headers': {
                            'content-type': 'application/json',
                            'authorization': nonadmin_auth_string,
                        },
                        'data': {
                            'username': username,
                            'password': password,
                            'email': email,
                            'is_staff': is_staff,
                        },
                        'status': 403,
                    },

                    # Test user creation as an administrator:
                    {
                        'name': 'create new user as admin',
                        'url': reverse(self.version + ':user-list'),
                        'method': 'POST',
                        'request_headers': {
                            'content-type': 'application/json',
                            'authorization': admin_auth_string,
                        },
                        'data': {
                            'username': username,
                            'password': password,
                            'email': email,
                            'is_staff': is_staff,
                        },
                        'status': 201,
                    },

                    # Test retrieval of a newly created user's profile info as
                    # an administrator:
                    {
                        'name': 'fetch new user as admin',
                        'url': '$HISTORY["create new user as admin"].$LOCATION',
                        'request_headers': {
                            'authorization': admin_auth_string,
                        },
                        'status': 200,
                        'response_json_paths': {
                            '$.username': username,
                            '$.email': email,
                            '$.is_staff': is_staff,
                        },
                    },

                    # Test retrieval of a newly created user's profile info as
                    # the retrieved user:
                    {
                        'name': 'fetch new user as self',
                        'url': '$HISTORY["create new user as admin"].$LOCATION',
                        'request_headers': {
                            'authorization': new_user_auth_string,
                        },
                        'status': 200,
                        'response_json_paths': {
                            '$.username': username,
                            '$.email': email,
                            '$.is_staff': is_staff,
                        },
                    },

                    # Test failure on attempt to retrieve the new user's profile
                    # info as another non-administrator user:
                    {
                        'name': 'fail fetch new user as nonadmin',
                        'url': '$HISTORY["create new user as admin"].$LOCATION',
                        'request_headers': {
                            'authorization': nonadmin_auth_string,
                        },
                        'status': 403,
                    },

                ],
            },
        )
