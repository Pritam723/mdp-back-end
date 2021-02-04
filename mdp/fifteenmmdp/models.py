from django.db import models
from .validators import validate_file_extension

# Create your models here.

def upload_path(instance, filname):
    return '/'.join(['covers', str(instance.title), filname])

class AllMeterFiles(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.CharField(max_length=255)
    month = models.CharField(max_length=255)
    zippedMeterFile = models.FileField(upload_to='media',validators=[validate_file_extension])
    dirStructure = models.TextField(null=True) # JSON-serialized (text) version of your list

    def __str__(self):
        return("All meter data for " + self.year + " and " + self.month)
    
    def myId(self):
        return self.id




# class Book(models.Model):
#     title = models.CharField(max_length=32, blank=False)
#     cover = models.ImageField(blank=True, null=True, upload_to=upload_path)