from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .authentication import freelancer_only, client_only
from .models import Application
from .serializers import ApplicationSerializer


@api_view(['POST'])
@freelancer_only
def apply_job(request):
    serializer = ApplicationSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors)



@api_view(['GET'])
@client_only
def view_applications(request, job_id):
    applications = Application.objects.filter(job_id=job_id)
    serializer = ApplicationSerializer(applications, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@client_only
def accept_application(request):
    application_id = request.data.get("application_id")

    try:
        application = Application.objects.get(id=application_id)
        application.status = "accepted"
        application.save()

        return Response({"message": "Application accepted"})

    except Application.DoesNotExist:
        return Response(
            {"error": "Application not found"}
        )



@api_view(['POST'])
@client_only
def reject_application(request):
    application_id = request.data.get("application_id")
    try:
        application = Application.objects.get(id=application_id)
        application.status = "rejected"
        application.save()

        return Response({"message": "Application rejected"})

    except Application.DoesNotExist:
        return Response(
            {"error": "Application not found"}
        )
