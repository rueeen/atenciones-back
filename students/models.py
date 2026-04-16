from django.db import models
from organization.models import Career


class Student(models.Model):
    full_name = models.CharField(max_length=200)
    rut = models.CharField(max_length=12, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    career = models.ForeignKey(Career, on_delete=models.PROTECT, related_name='students')
    schedule = models.CharField(max_length=60, blank=True)
    observations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f'{self.full_name} ({self.rut})'
