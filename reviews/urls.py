from api.urls import router
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_swagger.views import get_swagger_view


urlpatterns = [

    # Django admin site:
    url(
        regex=r'^admin/',
        view=admin.site.urls,
    ),

    # Django REST Framework browsable API authentication:
    url(
        regex=r'^api-auth/',
        view=include(
            'rest_framework.urls',
            namespace='rest_framework'
        ),
    ),

    # Django REST Framework token authentication:
    url(
        regex=r'^api-token-auth/',
        view=obtain_auth_token,
    ),

    # JSON Web Token session-like authentication:

    url(
        regex=r'^jwt/auth/?',
        view=obtain_jwt_token,
    ),

    url(
        regex=r'^jwt/refresh/?',
        view=refresh_jwt_token,
    ),

    # Swagger API documentation:
    url(
        regex=r'^$',
        view=get_swagger_view(
            title='Reviews API',
        ),
    ),

    # API routes proper:
    url(
        regex=r'^v1/',
        view=include(
            router.urls,
            namespace='v1',
        ),
    ),

]


# Enable the Django debug toolbar URLs only when running with debugging enabled:
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(
            regex=r'^debug_toolbar/',
            view=include(
                debug_toolbar.urls,
            ),
        ),
    ]
