from dry_rest_permissions.generics import DRYPermissionFiltersBase


class UserFilterBackend(DRYPermissionFiltersBase):
    '''
    Override the default queryset so that regular, non-administrator users can
    only see their own user profile; only administrators can see all users.
    '''

    def filter_list_queryset(self, request, queryset, view):

        if request.user.is_staff:
            return queryset

        return queryset.filter(
            username=request.user.username,
        )


class ReviewFilterBackend(DRYPermissionFiltersBase):
    '''
    Override the default queryset so that regular, non-administrator users can
    only see reviews they submitted themselves; only administrators can see all
    reviews.
    '''

    def filter_list_queryset(self, request, queryset, view):

        if request.user.is_staff:
            return queryset

        return queryset.filter(
            submitter=request.user,
        )
