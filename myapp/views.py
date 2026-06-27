from django.conf import settings
from django.db import transaction
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import CustomJWTAuthentication
from .models import Application
from .role_permissions import IsClient, IsFreelancer
from .serializers import ApplicationSerializer, InternalApplicationListSerializer
from .permissions.internal_service import IsInternalService
import requests
import logging
from rest_framework.exceptions import ValidationError
from labora_shared.notification_client import (
    send_notification
)

logger = logging.getLogger(__name__)

# ==================================================
# FREELANCER CREATE APPLICATION
# ==================================================
class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFreelancer]

def perform_create(self, serializer):

    job_id = serializer.validated_data["job_id"]

    try:
        response = requests.get(
            f"{settings.JOB_SERVICE_URL}/api/internal/jobs/{job_id}/",
            headers={
                "X-Service-Key": settings.SERVICE_API_KEY
            },
            timeout=5
        )

        response.raise_for_status()

        job_data = response.json()

    except requests.RequestException:
        raise ValidationError(
            {"job_id": "Unable to verify job."}
        )

    if job_data.get("status") != "open":
        raise ValidationError(
            {"job_id": "This job is not accepting applications."}
        )

    application = serializer.save(
        freelancer_id=self.request.user.id,
        client_id=job_data["client_id"]
    )

    send_notification(
        user_id=application.client_id,
        notification_type="application_received",
        title="New Application",
        message="A freelancer applied to your job.",
        payload={
            "job_id": application.job_id,
            "application_id": application.id,
            "freelancer_id": application.freelancer_id
        }
    )

# ==================================================
# FREELANCER VIEW OWN APPLICATIONS
# ==================================================

class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFreelancer]

    def get_queryset(self):
        return Application.objects.filter(
            freelancer_id=self.request.user.id
        ).order_by("-created_at")


# ==================================================
# CLIENT VIEW APPLICATIONS FOR A JOB
# ==================================================

class JobApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsClient]

    def get_queryset(self):
        return Application.objects.filter(
            job_id=self.kwargs["job_id"]
        ).order_by("-created_at")


# ==================================================
# CLIENT ACCEPT APPLICATION
# ==================================================

class AcceptApplicationView(APIView):

    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsClient]

    def patch(self, request, application_id):

        try:

            with transaction.atomic():

                application = (
                    Application.objects
                    .select_for_update()
                    .get(id=application_id)
                )

                if application.client_id != request.user.id:
                    return Response(
                        {"error": "Not authorized"},
                        status=status.HTTP_403_FORBIDDEN
                    )

                if application.status != "pending":
                    return Response(
                        {
                            "error":
                                f"Application already {application.status}"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                job_response = requests.patch(
                    f"{settings.JOB_SERVICE_URL}/api/internal/jobs/{application.job_id}/status/",
                    headers={
                        "X-Service-Key": settings.SERVICE_API_KEY
                    },
                    json={
                        "status": "in_progress"
                    },
                    timeout=5
                )

                job_response.raise_for_status()

                chatroom_response = requests.post(
                    f"{settings.MESSAGE_SERVICE_URL}/api/internal/chatrooms/create/",
                    headers={
                        "X-Service-Key": settings.SERVICE_API_KEY
                    },
                    json={
                        "job_id": application.job_id,
                        "client_id": application.client_id,
                        "freelancer_id": application.freelancer_id
                    },
                    timeout=5
                )

                chatroom_response.raise_for_status()

              

                application.status = "accepted"
                application.save(
                    update_fields=[
                        "status",
                        "updated_at"
                    ]
                )
                Application.objects.filter(
                    job_id=application.job_id,
                    status="pending"
                ).exclude(
                    id=application.id
                ).update(
                    status="rejected"
                )

                try:
                    send_notification(
                        user_id=application.freelancer_id,
                        notification_type="proposal_accepted",
                        title="Proposal Accepted",
                        message="Your proposal has been accepted.",
                        payload={
                            "job_id": application.job_id,
                            "application_id": application.id
                        }
                    )

                except Exception:
                    logger.exception(
                        "Failed to send proposal accepted notification "
                        "for application %s",
                        application.id
                    )

            return Response(
                {
                    "message": "Application accepted",
                    "application_id": application.id
                },
                status=status.HTTP_200_OK
            )

        except Application.DoesNotExist:

            return Response(
                {
                    "error": "Application not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except requests.RequestException as e:

            logger.exception(
                "Internal service communication failed: %s",
                str(e)
            )

            return Response(
                {
                    "error":
                        "Failed to complete acceptance workflow"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:

            logger.exception(
                "Unexpected error while accepting application: %s",
                str(e)
            )

            return Response(
                {
                    "error":
                        "An unexpected error occurred"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# ==================================================
# CLIENT REJECT APPLICATION
# ==================================================

class RejectApplicationView(APIView):

    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsClient]

    def patch(self, request, application_id):

        try:
            application = Application.objects.get(
                id=application_id
            )

        except Application.DoesNotExist:
            return Response(
                {"error": "Application not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if application.client_id != request.user.id:
            return Response(
                {"error": "Not authorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        if application.status != "pending":
            return Response(
                {
                    "error":
                    f"Application already {application.status}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        application.status = "rejected"
        application.save()
        try:
            response = send_notification(
                user_id=application.freelancer_id,
                notification_type="proposal_rejected",
                title="Proposal Rejected",
                message="Your proposal was rejected.",
                payload={
                    "job_id": application.job_id,
                    "application_id": application.id
                }
            )

        except Exception as e:
            logger.exception(
                "Failed to send 'proposal_rejected' notification for application %s: %s",
                application.id,
                str(e)
            )

        return Response(
            {
                "message": "Application rejected",
                "application_id": application.id
            },
            status=status.HTTP_200_OK
        )
# ==================================================
# FREELANCER WITHDRAW APPLICATION
# ==================================================

class WithdrawApplicationView(APIView):

    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFreelancer]

    def patch(self, request, application_id):

        try:
            application = Application.objects.get(
                id=application_id,
                freelancer_id=request.user.id
            )

        except Application.DoesNotExist:
            return Response(
                {"error": "Application not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if application.status != "pending":
            return Response(
                {
                    "error":
                    "Only pending applications can be withdrawn"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        application.status = "withdrawn"
        application.save()

        return Response(
            {
                "message": "Application withdrawn",
                "application_id": application.id
            },
            status=status.HTTP_200_OK
        )


class InternalJobFreelancerView(APIView):
    authentication_classes = []
    permission_classes = [IsInternalService]

    def get(self, request, job_id):

        application = (
            Application.objects
            .filter(job_id=job_id)
            .first()
        )

        if not application:

            return Response(
                {
                    "error": "No application found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "freelancer_id": application.freelancer_id
            }
        )


class InternalApplicationListView(APIView):
    authentication_classes = []
    permission_classes = [IsInternalService]

    def get(self, request):

        applications = Application.objects.all().order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 20

        page = paginator.paginate_queryset(
            applications,
            request
        )

        serializer = InternalApplicationListSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )


class InternalApplicationStatsView(APIView):
    authentication_classes = []
    permission_classes = [IsInternalService]

    def get(self, request):

        return Response({

            "total_applications": Application.objects.count(),

            "pending_applications": Application.objects.filter(
                status="pending"
            ).count(),

            "accepted_applications": Application.objects.filter(
                status="accepted"
            ).count(),

            "rejected_applications": Application.objects.filter(
                status="rejected"
            ).count(),

            "withdrawn_applications": Application.objects.filter(
                status="withdrawn"
            ).count(),

        })


class InternalApplicationDetailView(APIView):
    authentication_classes = []
    permission_classes = [IsInternalService]

    def get(self, request, application_id):

        try:

            application = Application.objects.get(
                pk=application_id
            )

        except Application.DoesNotExist:

            return Response(
                {
                    "error": "Application not found"
                },
                status=404
            )

        serializer = InternalApplicationListSerializer(
            application
        )

        return Response(
            serializer.data

        )
