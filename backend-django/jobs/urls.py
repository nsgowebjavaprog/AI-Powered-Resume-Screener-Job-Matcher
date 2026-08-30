"""
jobs/urls.py
------------
DRF's `DefaultRouter` auto-generates all the standard CRUD URL patterns
for each ViewSet (list/create/retrieve/update/delete + our custom @action).
This is why you rarely hand-write `path()` for CRUD resources in DRF.
"""
from rest_framework.routers import DefaultRouter
from .views import JobPostingViewSet, ResumeViewSet, MatchResultViewSet

router = DefaultRouter()
router.register("jobs", JobPostingViewSet, basename="job")
router.register("resumes", ResumeViewSet, basename="resume")
router.register("match-results", MatchResultViewSet, basename="matchresult")

urlpatterns = router.urls
