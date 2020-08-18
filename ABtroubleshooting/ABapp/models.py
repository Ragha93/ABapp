from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.core.validators import MinLengthValidator

class Userinfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    team_name = models.CharField(max_length=100,blank=False)
    register_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

class AB_troubleshooting(models.Model):
    asin = models.SlugField(max_length=10,validators=[MinLengthValidator(10)], verbose_name="ASIN")
    vendorcode = models.CharField(max_length=6)
    taskid = models.IntegerField(default='1993')
    allocatedto = models.CharField(max_length=20)
    runby = models.CharField(max_length=20, default=User, blank=False)
    allocationdate = models.DateField(max_length=100,default=timezone.now)
    loadtime = models.TimeField(max_length=100,default=timezone.now)
    runstatus = models.CharField(max_length=20,null=True,blank=True,default="run")
    # Add task id, change the uniqueness of the ASIN

    def publish(self):
        self.runstatus = "Complete"
        self.save()
    # Add task id, change the uniqueness of the ASIN

    def __str__(self):
        return self.asin +","+ self.allocatedto

class AB_data(models.Model):
    asin = models.SlugField(max_length=10,validators=[MinLengthValidator(10)])
    #Buyability Analyzer#######################################################
    buyability_status = models.CharField(max_length=200, null=True, blank=True)
    Item = models.CharField(max_length=200,null=True,blank=True)
    Contribution = models.CharField(max_length=200,null=True,blank=True)
    Price_OLSListing = models.CharField(max_length=200,null=True,blank=True)
    Price_BUYListing = models.CharField(max_length=200,null=True,blank=True)
    Xref = models.CharField(max_length=200,null=True,blank=True)
    Shipping_cost = models.CharField(max_length=200,null=True,blank=True)
    AvailabilityGpi = models.CharField(max_length=200,null=True,blank=True)
    Offer_Blacklist = models.CharField(max_length=200,null=True,blank=True)
    Seller_Suppression = models.CharField(max_length=200,null=True,blank=True)
    Explicit_Settlement = models.CharField(max_length=200,null=True,blank=True)
    Backend_buyability = models.CharField(max_length=200,null=True,blank=True)
    bossed_user = models.CharField(max_length=300,null=True,blank=True)
    bossed_reason = models.CharField(max_length=300,null=True,blank=True)
    #Buyability Analyzer#######################################################
    #sourceability############################################################
    sourceability_status = models.CharField(max_length=200,null=True,blank=True)
    sourceability_reason = models.CharField(max_length=100,null=True,blank=True)
    #sourceability############################################################
    #procurability############################################################
    procurability_status = models.CharField(max_length=200,null=True,blank=True)
    procurability_explanation = models.CharField(max_length=200,null=True,blank=True)
    #procurability############################################################
    #IPCplanpreview###########################################################
    IPCstatus = models.CharField(max_length=200,null=True,blank=True)
    # sourcinginstockstatus = models.CharField(max_length=200,null=True,blank=True)
    InStock_status= models.CharField(max_length=200,null=True,blank=True)
    Vendorcode= models.CharField(max_length=200,null=True,blank=True)
    Reason= models.CharField(max_length=200,null=True,blank=True)
    Ipc_status_reason = models.CharField(max_length=200,null=True,blank=True)
    #IPCplanpreview###########################################################
    allocatedto = models.CharField(max_length=20,null=True,blank=True)
    allocationdate = models.DateField(max_length=100,default=timezone.now)
    runtime = models.TimeField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.asin

class AB_template(models.Model):
    asin = models.SlugField(max_length=10,validators=[MinLengthValidator(10)], unique=True, verbose_name="ASIN")
    vendorcode = models.CharField(max_length=6)
    taskid = models.IntegerField(default='1993')
    allocatedto = models.CharField(max_length=20)
    runby = models.CharField(max_length=20, default=User, blank=False)
    allocationdate = models.DateField(max_length=100,default=timezone.now)
    loadtime = models.TimeField(max_length=100,default=timezone.now)

class AB_sitestatus(models.Model):
    asin = models.SlugField(max_length=10,validators=[MinLengthValidator(10)], unique=True, verbose_name="ASIN")
    sitestatus = models.CharField(max_length=20)
    allocatedto = models.CharField(max_length=20)

class Hcsavings(models.Model):
    toolname = models.CharField(max_length=20)
    toolcompletiondate = models.DateField(max_length=10)
    hcsavings = models.FloatField()

    def __str__(self):
        return self.toolname
