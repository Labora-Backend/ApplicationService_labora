from django.db import models


class Application(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("withdrawn", "Withdrawn"),
    )

    job_id = models.IntegerField()

    client_id = models.IntegerField()

    freelancer_id = models.IntegerField()

    cover_letter = models.TextField()

    proposed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    delivery_time_days = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = (
            "job_id",
            "freelancer_id"
        )

    def __str__(self):
        return (
            f"Application #{self.id} "
            f"for Job {self.job_id}"
        )


class ProposalMessage(models.Model):

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender_id = models.IntegerField()

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"Message #{self.id}"
        )