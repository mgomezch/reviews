from rest_framework.routers import DefaultRouter

from api.views import (
    UserViewSet,
    CompanyViewSet,
    ReviewViewSet,
    ReviewerViewSet,
)


class Router(DefaultRouter):

    # Format suffixes break lookup fields in resource URIs if they happen to
    # include dots.  Suffixing the `format` query parameter accomplishes easy
    # format selection without breaking routes, so nothing important is lost by
    # disabling this feature.
    include_format_suffixes = False


router = Router(
    trailing_slash=False,
)

router.register('user', UserViewSet)
router.register('company', CompanyViewSet)
router.register('reviewer', ReviewerViewSet)
router.register('review', ReviewViewSet)
