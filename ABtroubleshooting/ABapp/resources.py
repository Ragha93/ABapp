from import_export import resources
from ABapp.models import AB_troubleshooting,AB_data,AB_template,AB_sitestatus

class ABResource(resources.ModelResource):
    class Meta:
        model = AB_troubleshooting

class ABoutput(resources.ModelResource):
    class Meta:
        model = AB_data

class ABtemplate(resources.ModelResource):
    class Meta:
        model = AB_template
        fields = 'asin','vendorcode','taskid','allocatedto','runby'

class ABsite(resources.ModelResource):
    class Meta:
        model = AB_sitestatus
