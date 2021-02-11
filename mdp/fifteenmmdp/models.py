from django.db import models
from .validators import validate_file_extension,validate_file_extension_npc
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
# Create your models here.

def upload_path(instance, filename):
    return '/'.join(['meterFile', str(instance.year),str(instance.month), filename])



class AllMeterFiles(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.CharField(max_length=255)
    month = models.CharField(max_length=255)
    zippedMeterFile = models.FileField(upload_to = upload_path,validators=[validate_file_extension],max_length=1023)
    dirStructure = models.TextField(null=True) # JSON-serialized (text) version of your list
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.SET_NULL)
    # status = models.CharField(max_length=255)     
    # {'Uploaded' , 'Extracted' , 'Merged' ,'Verified', 'DateFiltered', 'MWHCreated', 'FictCreated' , 'FinalOutputCreated' }
    
    # def save(self,*args, **kwargs):
    #     self.added_by = request.user
    #     super().save(request,*args, **kwargs)

    def __str__(self):
        return("All meter data for " + self.year + " and " + self.month)
    
    def myId(self):
        return self.id

class OverwriteStorage(FileSystemStorage):
  
    def get_available_name(self, name,max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name
        
def upload_path_npc(instance, filename):
    # return '/'.join(['meterFile', filename])
    return instance.filePath

class NpcFile(models.Model):
    id = models.AutoField(primary_key=True)
    fileName = models.CharField(max_length=255)
    filePath = models.CharField(max_length=1023)
    meterFile = models.ForeignKey(AllMeterFiles, on_delete=models.CASCADE)
    npcFile = models.FileField(upload_to = upload_path_npc,validators=[validate_file_extension_npc],max_length=1023,storage=OverwriteStorage())

    def __str__(self):
        return self.filePath