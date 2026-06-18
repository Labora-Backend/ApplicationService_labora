from django.conf import settings
from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import CustomJWTAuthentication
from .models import Application
from .role_permissions import IsClient, IsFreelancer
from .serializers import ApplicationSerializer
from .permissions.internal_service import IsInternalService
import requests

from labora_shared.notification_client import (
    send_notification
)

# ==================================================
# FREELANCER CREATE APPLICATION
# ==================================================

class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFreelancer]

    def perform_create(self, serializer):

        application = serializer.save(
            freelancer_id=self.request.user.id
        )

        try:

            send_notification(
                user_id=application.client_id,
                notification_type="application_received",
                title="New Application",
                message="A freelancer has applied to your job.",
                payload={
                    "job_id": application.job_id,
                    "application_id": application.id
                }
            )

        except Exception as e:

            print(
                f"Notification Error: {e}"
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

        try:

            with transaction.atomic():

                # Reject any other accepted applications
                Application.objects.filter(
                    job_id=application.job_id,
                    status="accepted"
                ).exclude(
                    id=application.id
                ).update(
                    status="rejected"
                )

                application.status = "accepted"
                application.save()

                response = requests.post(
                    f"{settings.MESSAGE_SERVICE_URL}/api/internal/chatrooms/create/",
                    headers={
                        "X-Service-Key":
                            settings.SERVICE_API_KEY
                    },
                    json={
                        "job_id":
                            application.job_id,

                        "client_id":
                            application.client_id,

                        "freelancer_id":
                            application.freelancer_id,
                    },
                    timeout=5
                )

                response.raise_for_status()

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

                except Exception as e:
                    print(
                        f"Notification Error: {e}"
                    )

        except requests.exceptions.RequestException as e:

            return Response(
                {
                    "error":
                    f"Failed to create chat room: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:

            return Response(
                {
                    "error":
                    str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "message": "Application accepted",
                "application_id": application.id
            },
            status=status.HTTP_200_OK
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
            send_notification(
                user_id=application.freelancer_id,
                notification_type="proposal_rejected",
                title="Proposal Rejected",
                message="Unfortunately, your proposal was not selected.",
                payload={
                    "job_id": application.job_id,
                    "application_id": application.id
                }
            )

        except Exception as e:
            print(
                f"Notification Error: {e}"
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