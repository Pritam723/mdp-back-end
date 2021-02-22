from django.contrib import admin
from .models import AllMeterFiles,NpcFile,MergedFile,DateFilteredFile,ValidatedFile,RealMeterMWHFile

# Register your models here.


admin.site.register(AllMeterFiles)
admin.site.register(NpcFile)
admin.site.register(MergedFile)
admin.site.register(DateFilteredFile)
admin.site.register(ValidatedFile)
admin.site.register(RealMeterMWHFile)