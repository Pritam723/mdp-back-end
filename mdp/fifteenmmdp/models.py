from django.db import models
from .validators import validate_file_extension
from django.conf import settings

# Create your models here.

def upload_path(instance, filename):
    return '/'.join(['meterFile', str(instance.year),str(instance.month), filename])

class AllMeterFiles(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.CharField(max_length=255)
    month = models.CharField(max_length=255)
    zippedMeterFile = models.FileField(upload_to = upload_path,validators=[validate_file_extension])
    dirStructure = models.TextField(null=True) # JSON-serialized (text) version of your list
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)
    
    # def save(self,*args, **kwargs):
    #     self.added_by = request.user
    #     super().save(request,*args, **kwargs)

    def __str__(self):
        return("All meter data for " + self.year + " and " + self.month)
    
    def myId(self):
        return self.id





# class Book(models.Model):
#     title = models.CharField(max_length=32, blank=False)
#     cover = models.ImageField(blank=True, null=True, upload_to=upload_path)