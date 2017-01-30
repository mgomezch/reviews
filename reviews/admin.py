from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from reviews.models import (
    Company,
    Review,
    Reviewer,
    User,
)


admin.site.register(User, UserAdmin)

for model in [
    Company,
    Review,
    Reviewer,
]:
    admin.site.register(model)
