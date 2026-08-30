from django.contrib import admin
from .models import JobPosting, Resume, MatchResult

# admin.site.register gives instant CRUD screens for these models at /admin/
admin.site.register(JobPosting)
admin.site.register(Resume)
admin.site.register(MatchResult)
