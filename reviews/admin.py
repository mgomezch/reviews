from django.contrib import admin
from reviews.models import (
    Company,
    Review,
    Reviewer,
    User,
)


for model in [
    Company,
    Review,
    Reviewer,
    User,
]:
    admin.site.register(model)
