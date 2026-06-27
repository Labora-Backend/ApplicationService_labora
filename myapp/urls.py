
from django.urls import path

from .views import (
    ApplicationCreateView,
    MyApplicationsView,
    JobApplicationsView,
    AcceptApplicationView,
    RejectApplicationView,
    WithdrawApplicationView, InternalJobFreelancerView, InternalApplicationListView, InternalApplicationStatsView,
    InternalApplicationDetailView,
)

urlpatterns = [

    # freelancer
    path(
        "applications/create/",
        ApplicationCreateView.as_view(),
        name="create-application"
    ),

    path(
        "applications/my/",
        MyApplicationsView.as_view(),
        name="my-applications"
    ),

    path(
        "applications/<int:application_id>/withdraw/",
        WithdrawApplicationView.as_view(),
        name="withdraw-application"
    ),

    # client
    path(
        "applications/jobs/<int:job_id>/applications/",
        JobApplicationsView.as_view(),
        name="job-applications"
    ),

    path(
        "applications/<int:application_id>/accept/",
        AcceptApplicationView.as_view(),
        name="accept-application"
    ),

    path(
        "applications/<int:application_id>/reject/",
        RejectApplicationView.as_view(),
        name="reject-application"
    ),
path(
    "internal/jobs/<int:job_id>/freelancer/",
    InternalJobFreelancerView.as_view(),
    name="internal-job-freelancer"
),
    path(
        "internal/applications/",
        InternalApplicationListView.as_view()
    ),

    path(
        "internal/applications/stats/",
        InternalApplicationStatsView.as_view()
    ),

    path(
        "internal/applications/<int:application_id>/",
        InternalApplicationDetailView.as_view()
    ),




]