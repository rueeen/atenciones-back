from django.db import models


class Area(models.Model):
    name = models.CharField(max_length=120, unique=True)
    is_academic_direction = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class AcademicArea(models.Model):
    name = models.CharField(max_length=160, unique=True)
    parent_area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='academic_areas')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Career(models.Model):
    name = models.CharField(max_length=180, unique=True)
    academic_area = models.ForeignKey(AcademicArea, on_delete=models.PROTECT, related_name='careers')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
