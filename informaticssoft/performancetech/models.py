from django.db import models


class Section(models.Model):
    section_name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.section_name

class FileInStorage(models.Model):
    file_name = models.CharField(max_length=122)
    file_type = models.CharField(max_length=122)
    path = models.CharField(max_length=255)
    load_date = models.DateField()
    load_time = models.TimeField()
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    def __str__(self):
        return f'[{self.file_type}] {self.file_name}'