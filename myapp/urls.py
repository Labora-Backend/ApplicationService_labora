
from django.urls import path
from myapp import views

urlpatterns = [
    path("freelancer/jobs/apply/",views.apply_job),
    path("client/applications/<int:job_id>/",views.view_applications),
    path("client/applications/accept/",views.accept_application),
    path("client/applications/reject/",views.reject_application),
]