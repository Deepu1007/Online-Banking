from django.db import models
from django.contrib.auth.models import User

TICKET_STATUS = (
    ('OPEN', 'Open'),
    ('INP', 'In Progress'),
    ('RES', 'Resolved'),
    ('CLS', 'Closed'),
)

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=TICKET_STATUS, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} ({self.get_status_display()})"
