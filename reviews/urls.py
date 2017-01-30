from api.urls import router
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token


urlpatterns = [

    # Django admin site:
    url(r'^admin/?', admin.site.urls),

    # Django built-in authentication:
    url(
        '^',
        include('django.contrib.auth.urls'),
    ),

    # Django REST Framework browsable API authentication:
    url(
        r'^api-auth/',
        include(
            'rest_framework.urls',
            namespace='rest_framework'
        ),
    ),

    # Django REST Framework token authentication:
    url(r'^api-token-auth/', obtain_auth_token),

    # JSON Web Token session-like authentication:
    url(r'^jwt/auth/?', obtain_jwt_token),
    url(r'^jwt/refresh/?', refresh_jwt_token),

    # API routes proper:
    url(
        r'^v1/',
        include(
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
            r'^debug_toolbar/',
            include(
                debug_toolbar.urls
            )
        ),
    ]
