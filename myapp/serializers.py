from rest_framework import serializers
from .models import Application,ProposalMessage

from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Application

        fields = [
            "id",
            "job_id",
            "client_id",
            "freelancer_id",
            "cover_letter",
            "proposed_amount",
            "delivery_time_days",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "client_id",
            "freelancer_id",
            "status",
            "created_at",
            "updated_at",
        ]

class ProposalMessageSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = ProposalMessage

        fields = [
            "id",
            "application",
            "sender_id",
            "message",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "sender_id",
            "created_at",
        ]
from rest_framework import serializers

from .models import Application


class InternalApplicationListSerializer(serializers.ModelSerializer):

    class Meta:

        model = Application

        fields = [

            "id",

            "job_id",

            "client_id",

            "freelancer_id",

            "proposed_amount",

            "delivery_time_days",

            "status",

            "created_at",

        ]