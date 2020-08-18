from django.contrib import admin
from ABapp.models import AB_troubleshooting,Userinfo,User,AB_data,AB_template,AB_sitestatus,Hcsavings
from import_export.admin import ImportExportModelAdmin

admin.site.register(Userinfo)
# admin.site.register(AB_data)
admin.site.register(AB_template)
admin.site.register(AB_sitestatus)

@admin.register(Hcsavings)
class HCdata(ImportExportModelAdmin,admin.ModelAdmin):
        list_filter = ['toolname']
        class Meta:
            pass

@admin.register(AB_data)
class ABdata(ImportExportModelAdmin,admin.ModelAdmin):
        search_fields = ['asin']
        list_filter = ['allocatedto','allocationdate','buyability_status']
        class Meta:
            pass

@admin.register(AB_troubleshooting)
class ABtroubleshooting(ImportExportModelAdmin,admin.ModelAdmin):
        search_fields = ['asin']
        list_filter = ['allocationdate','allocatedto','runby']
        class Meta:
            pass
