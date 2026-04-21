from django.db import models


class Area(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class AcademicArea(models.Model):
    name = models.CharField(max_length=150, unique=True)
    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        related_name='academic_areas'
    )

    def __str__(self):
        return self.name


class Career(models.Model):
    name = models.CharField(max_length=150, unique=True)
    academic_area = models.ForeignKey(
        AcademicArea,
        on_delete=models.CASCADE,
        related_name='careers'
    )

    def __str__(self):
        return self.name
