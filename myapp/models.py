from django.db import models

class Application(models.Model):
    job_id = models.IntegerField()
    freelancer_id = models.IntegerField()
    cover_letter = models.TextField()
    proposed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time_days = models.IntegerField()
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
