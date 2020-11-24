from django.shortcuts import render
from ABapp.models import AB_troubleshooting,AB_data,AB_template,AB_sitestatus,Hcsavings
from django.http import HttpResponse,HttpResponseRedirect
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from ABapp.forms import Registrationdata,Registrationinfo,ABstore,ABstoredata,ABsitestatus
import concurrent.futures
from tablib import Dataset
from . import models
from ABapp.resources import ABResource,ABoutput,ABtemplate,ABsite
from django.views.generic import (View,TemplateView,
                                ListView,DetailView,
                                CreateView,DeleteView,UpdateView)
import requests
import pandas as pd
import numpy as np
import seaborn as sns
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import getpass
import concurrent.futures
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time,re,json
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect

@method_decorator(login_required, name='dispatch')
class Buyablestatusall(ListView):
    context_object_name = 'buyable'
    template_name = 'buyablestatusall.html'
    model = models.AB_data


# Home page ####################################################################
class Homepage(TemplateView):
    template_name = 'index.html'
# Home page ####################################################################

# Home page - Login ############################################################
@login_required
def index(request):
    return render(request,'base.html')
# Home page - Login ############################################################

# Registration #################################################################
def Registration(request):
    registered = False
    if request.method == 'POST':
        registeruser = Registrationinfo(data=request.POST)
        registerinfo = Registrationdata(data=request.POST)
        if registeruser.is_valid() and registerinfo.is_valid():
            registerus = registeruser.save()
            registerus.set_password(registerus.password)
            registerus.is_active = False
            registerus.save()
            registerinf = registerinfo.save(commit=False)
            registerinf.user = registerus
            registerinf.save()
            registered = True
            print("A new user {a} has registered at {b}".format(a = registerus.username,b = timezone.now()))
        else:
            print(registeruser.errors,registerinfo.errors)
    else:
            registeruser = Registrationinfo()
            registerinfo = Registrationdata()
    data_dict = {'registeruser':registeruser, 'registerinfo':registerinfo, 'registered':registered}
    return render(request, 'registration.html', context=data_dict)
# Registration #################################################################

# Login ########################################################################
def log_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username = username, password = password)
        if user and user.is_authenticated:
            if user.is_active:
                login(request, user)
                print("The user {} has logged-in at {}".format(username, timezone.now()))
                return HttpResponseRedirect(reverse(index))
            else:
                return HttpResponse("<h1> <em> <b> Your account is not active, contact @kragha </b> </em> </h1>")
        else:
            print("The user {} tried to login at {} with {}".format(username, timezone.now(), password))
            return HttpResponse("<h1> <em> <b> Register to login </b> </em> </h1>")
    else:
        return render(request, 'login.html')
# Login ########################################################################

# Logout #######################################################################
@login_required
def logguserout(request):
    logout(request)
    return render(request,'index.html')
# Logout #######################################################################

# Loading Excel file ###########################################################
def simple_upload(request):
    uploaded = False
    if request.method == 'POST':
        AB_input = ABResource()
        dataset = Dataset()
        input_data = request.FILES['myfile']
        imported_data = dataset.load(input_data.read())
        result = AB_input.import_data(dataset, dry_run=True)  # Test the data import
        if not result.has_errors():
            AB_input.import_data(dataset, dry_run=False)  # Actually import now
            uploaded = True
        else:
            return HttpResponseRedirect(reverse('Error'))
    else:
        AB_input = ABResource()
        dataset = Dataset()
    return render(request, 'ABappinput.html',{'uploaded':uploaded})
# Loading Excel file ###########################################################

@method_decorator(login_required, name='dispatch')
class Error(TemplateView):
    template_name= 'error.html'


#RUN page#######################################################################
@method_decorator(login_required, name='dispatch')
class Runpage(TemplateView):
    template_name = 'run.html'
#RUN page#######################################################################

#Password#######################################################################
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect(index)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'input.html', {
        'form': form
    })
#Password#######################################################################


def export(request):
    ABoutput1_resource = ABoutput()
    current = request.user
    date = timezone.localtime()
    data = AB_data.objects.all().filter(allocatedto=current).filter(allocationdate=date).order_by('-runtime')
    dataset = ABoutput1_resource.export(data)
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="@kragha_@harrishm_projects_AB_data.csv"'
    return response

def exportall(request):
    ABoutput2_resource = ABoutput()
    date = timezone.localtime()
    current = request.user
    data = AB_data.objects.all().filter(allocationdate=date).order_by('-runtime')
    dataset = ABoutput2_resource.export(data)
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="@kragha_@harrishm_projects_AB_data.csv"'
    return response

def template(request):
    ABtemplate_resource = ABtemplate()
    current = request.user
    data = AB_template.objects.all()
    dataset = ABtemplate_resource.export(data)
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="@kragha_projects_template.csv"'
    return response

def kragha(request):
    db = ABstoredata()
    timer = timezone.localtime()
    check = "run"
    current = request.user
    Site = AB_troubleshooting.objects.filter(runby=current).filter(runstatus=check).values_list('asin','vendorcode','allocatedto','pk')
    xuser = getpass.getuser()
    opt = webdriver.ChromeOptions()
    opt.add_argument('--ignore-certificate-errors')
    opt.add_argument('--headless')
    prefs = {'download.default_directory': "C:\\Users\\" + xuser + "\\Desktop\\ESNP\\"}
    opt.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome("C:\Program Files (x86)\SeleniumWrapper\chromedriver.exe", options=opt)
    wait = WebDriverWait(driver, 600, poll_frequency=1)
    driver.implicitly_wait(20)
    remove = "['']"
    with concurrent.futures.ThreadPoolExecutor() as executor:
        num = 1
        total = Site.count()
        print(f"I am starting at {timer}")
        for (w,vv,uvw,pk) in Site:
            print("currently checking {}, {} out of {}".format(w,num,total))
            num = num + 1
            url2 = "URL".format(w)
            r = requests.get(url2)
            o = r.json()
            newdict = {"asin" : o['input']['asin'],"Result" :o['response']}
            if 'offerListingList' in o['response']:
                x = newdict['asin']
                y = "Live"
                newdict = {"asin" : x,"Result" : y}
                # New try
                # Sourceability and procurability
                driver.get('url'.format(newdict['asin']))
                x = driver.find_element_by_xpath("/html/body").text
                ww = str(re.findall(r'"statusReasonCode":"(.*?)"', x)).strip(remove)
                xx = str(re.findall(r'"calculatedStatus":"(.*?)"', x)).strip(remove)

                driver.get('url'.format(asin=w,code=vv))
                x = driver.find_element_by_xpath("/html/body").text
                uu = str(re.findall(r'"sourceabilityReason":"(.*?)"', x)).strip(remove)
                vw = str(re.findall(r'"effectiveSourceabilityStatus":"(.*?)"', x)).strip(remove)

                # IPC
                ipc_dict = {}
                driver.get('url'.format(asin=w))
                xy = json.loads(driver.find_element_by_xpath("/html/body").text)
                try:
                    # 1 ASIN not found, no planning#####################################*************************************
                    if xy['response']['failure']:
                        ipc_dict = {'asin':w, 'Inventory':'No info on inventory', 'IPCstatus':xy['response']['failure']['failureType'],
                                    'IPCReason':xy['response']['failure']['failureMessage'] ,'Vendorcode':vv,
                                    'Reason':xy['response']['failure']['failureMessage']}
                        print('rule1')
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = "*"
                        data.Item = "*"
                        data.Contribution = "*"
                        data.Price_OLSListing = "*"
                        data.Price_BUYListing = "*"
                        data.Xref = "*"
                        data.AvailabilityGpi = "*"
                        data.Offer_Blacklist = "*"
                        data.Seller_Suppression = "*"
                        data.Explicit_Settlement = "*"
                        data.Backend_buyability = "*"
                        data.bossed_user = "*"
                        data.Shipping_cost = "*"
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')

                    elif xy['exception']:
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = xy['exception']['exceptionType']
                        data.Ipc_status_reason = xy['exception']['exceptionMsg']
                        data.Vendorcode = "*"
                        data.Reason = "*"
                        data.InStock_status = "*"
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = "*"
                        data.Item = "*"
                        data.Contribution = "*"
                        data.Price_OLSListing = "*"
                        data.Price_BUYListing = "*"
                        data.Xref = "*"
                        data.AvailabilityGpi = "*"
                        data.Offer_Blacklist = "*"
                        data.Seller_Suppression = "*"
                        data.Explicit_Settlement = "*"
                        data.Backend_buyability = "*"
                        data.bossed_user = "*"
                        data.Shipping_cost = "*"
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    #2 Planned #####################################False False Planned FC
                    elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSourcingOptionsFromVAR']==False and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSelectedSourcingOptions']==False and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['plannedFcs']:
                        abc = xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors']
                        abccount = len(abc)
                        for a in range(0,abccount):
                            if xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'] , 'IPCstatus':'Planned',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason'] ,'Vendorcode':vv,
                                            'Reason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']}
                            elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'], 'IPCstatus':'Not Planned',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['skippedReasons'] ,'Vendorcode':vv,
                                            'Reason': xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason']}
                        if not ipc_dict:
                            ipc_dict = {'asin':w, 'Inventory':'No info on inventory', 'IPCstatus':'Not Planned',
                                        'IPCReason':'Source vendorcode missing' ,'Vendorcode':vv,
                                        'Reason':'Check Vendor ASIN relations or SC - Rule 2'}
                        else:
                            print('rule2')
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = "*"
                        data.Item = "*"
                        data.Contribution = "*"
                        data.Price_OLSListing = "*"
                        data.Price_BUYListing = "*"
                        data.Xref = "*"
                        data.AvailabilityGpi = "*"
                        data.Offer_Blacklist = "*"
                        data.Seller_Suppression = "*"
                        data.Explicit_Settlement = "*"
                        data.Backend_buyability = "*"
                        data.bossed_user = "*"
                        data.Shipping_cost = "*"
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    #3 NotPlanned #####################################False False No planned FC
                    elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSourcingOptionsFromVAR']==False and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSelectedSourcingOptions']==False and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['plannedFcs']:
                        abc = xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors']
                        abccount = len(abc)
                        for a in range(0,abccount):
                            if xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and  xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'] , 'IPCstatus':'Planned',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason'] ,'Vendorcode':vv,
                                            'Reason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']}

                            elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'], 'IPCstatus':'Not Planned',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['skippedReasons'] ,'Vendorcode':vv,
                                            'Reason':'No planned FCs for this vendorCode - Rule 3'}
                        if not ipc_dict:
                            ipc_dict = {'asin':w, 'Inventory':'No info', 'IPCstatus':'Not Planned',
                                        'IPCReason':'Source vendorcode missing' ,'Vendorcode':vv,
                                        'Reason':'Check Vendor ASIN relations or SC - Rule 3'}
                        else:
                            print('rule3')
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = "*"
                        data.Item = "*"
                        data.Contribution = "*"
                        data.Price_OLSListing = "*"
                        data.Price_BUYListing = "*"
                        data.Xref = "*"
                        data.AvailabilityGpi = "*"
                        data.Offer_Blacklist = "*"
                        data.Seller_Suppression = "*"
                        data.Explicit_Settlement = "*"
                        data.Backend_buyability = "*"
                        data.bossed_user = "*"
                        data.Shipping_cost = "*"
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    #4No sourcing #####################################Flase True no planned FC
                    elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSourcingOptionsFromVAR']==False and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSelectedSourcingOptions']==True and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['plannedFcs']:
                        abc = xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors']
                        abccount = len(abc)
                        for a in range(0,abccount):
                            if xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and  xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'] , 'IPCstatus':'Planned',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason'] ,'Vendorcode':vv,
                                            'Reason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']}

                            elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'], 'IPCstatus':'NO_SOURCING_OPTION',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['skippedReasons'] ,'Vendorcode':vv,
                                            'Reason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason']}
                        if not ipc_dict:
                            ipc_dict = {'asin':w, 'Inventory':'No info', 'IPCstatus':'NO_SOURCING_OPTION',
                                        'IPCReason':'Source vendorcode missing' ,'Vendorcode':vv,
                                        'Reason':' Could not compute vendor TIL: No vendor available for planning for buyingIntent: PREDICTIVE,Check Vendor ASIN relations or SC -Rule 4'}
                        else:
                            print('rule4')
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.bossed_reason = "*"
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.Item = "*"
                        data.Contribution = "*"
                        data.Price_OLSListing = "*"
                        data.Price_BUYListing = "*"
                        data.Xref = "*"
                        data.AvailabilityGpi = "*"
                        data.Offer_Blacklist = "*"
                        data.Seller_Suppression = "*"
                        data.Explicit_Settlement = "*"
                        data.Backend_buyability = "*"
                        data.bossed_user = "*"
                        data.Shipping_cost = "*"
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    #5No sourcing #####################################Flase True  planned FC
                    elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSourcingOptionsFromVAR']==False and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSelectedSourcingOptions']==True and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['plannedFcs']:
                        abc = xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors']
                        abccount = len(abc)
                        for a in range(0,abccount):
                            if xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and  xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'] , 'IPCstatus':'Planned',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason'] ,'Vendorcode':vv,
                                            'Reason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']}

                            elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'], 'IPCstatus':'NO_SOURCING_OPTION',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['skippedReasons'] ,'Vendorcode':vv,
                                            'Reason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason']}
                        if not ipc_dict:
                            ipc_dict = {'asin':w, 'Inventory':'No info on inventory', 'IPCstatus':'NO_SOURCING_OPTION',
                                        'IPCReason':'Source vendorcode missing' ,'Vendorcode':vv,
                                        'Reason':' Could not compute vendor TIL: No vendor available for planning for buyingIntent: PREDICTIVE,Check Vendor ASIN relations or SC -Rule 5'}
                        else:
                            print('rule5')
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = "*"
                        data.Item ="*"
                        data.Contribution = "*"
                        data.Price_OLSListing = "*"
                        data.Price_BUYListing = "*"
                        data.Xref = "*"
                        data.AvailabilityGpi = "*"
                        data.Offer_Blacklist = "*"
                        data.Seller_Suppression = "*"
                        data.Explicit_Settlement = "*"
                        data.Backend_buyability = "*"
                        data.bossed_user = "*"
                        data.Shipping_cost = "*"
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    #6No sourcing #####################################True True  no planned FC*************************************
                    elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSourcingOptionsFromVAR']==True and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSelectedSourcingOptions']==True and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['plannedFcs']:
                        ipc_dict = {'asin':w, 'Inventory':'No info on inventory', 'IPCstatus':'NO_SOURCING_OPTION',
                                    'IPCReason':'No vendor available for planning for buyingIntent: PREDICTIVE' ,'Vendorcode':vv,
                                    'Reason':'Check Vendor Asin Relations - Rule 6'}

                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = "*"
                        data.Item = "*"
                        data.Contribution = "*"
                        data.Price_OLSListing = "*"
                        data.Price_BUYListing = "*"
                        data.Xref = "*"
                        data.AvailabilityGpi = "*"
                        data.Offer_Blacklist = "*"
                        data.Seller_Suppression = "*"
                        data.Explicit_Settlement = "*"
                        data.Backend_buyability = "*"
                        data.bossed_user = "*"
                        data.Shipping_cost = "*"
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    #7No sourcing #####################################True True  planned FC*************************************
                    elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSourcingOptionsFromVAR']==True and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSelectedSourcingOptions']==True and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['plannedFcs']:
                        ipc_dict = {'asin':w, 'Inventory':'No info on inventory', 'IPCstatus':'NO_SOURCING_OPTION',
                                    'IPCReason':'No vendor available for planning for buyingIntent: PREDICTIVE' ,'Vendorcode':vv,
                                    'Reason':'There are some planned FCs - Rule 7'}

                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = "*"
                        data.Item = "*"
                        data.Contribution = "*"
                        data.Price_OLSListing = "*"
                        data.Price_BUYListing = "*"
                        data.Xref = "*"
                        data.AvailabilityGpi = "*"
                        data.Offer_Blacklist = "*"
                        data.Seller_Suppression = "*"
                        data.Explicit_Settlement = "*"
                        data.Backend_buyability = "*"
                        data.bossed_user = "*"
                        data.Shipping_cost = "*"
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')

                except:
                    if xy['response']['buyingIntentToComputationContext']['IMPORT']:
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = "Import Vendord"
                        data.Ipc_status_reason = "Import Vendord"
                        data.Vendorcode = "Import Vendord"
                        data.Reason = "Import Vendord"
                        data.InStock_status = "Import Vendord"
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = "*"
                        data.Item = "*"
                        data.Contribution = "*"
                        data.Price_OLSListing = "*"
                        data.Price_BUYListing = "*"
                        data.Xref = "*"
                        data.AvailabilityGpi = "*"
                        data.Offer_Blacklist = "*"
                        data.Seller_Suppression = "*"
                        data.Explicit_Settlement = "*"
                        data.Backend_buyability = "*"
                        data.bossed_user = "*"
                        data.Shipping_cost = "*"
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    else:
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = "Exception :no response received, check manually"
                        data.Ipc_status_reason = "Exception :no response received, check manually"
                        data.Vendorcode = "Exception :no response received, check manually"
                        data.Reason = "Exception :no response received, check manually"
                        data.InStock_status = "Exception :no response received, check manually"
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = "*"
                        data.Item = "*"
                        data.Contribution = "*"
                        data.Price_OLSListing = "*"
                        data.Price_BUYListing = "*"
                        data.Xref = "*"
                        data.AvailabilityGpi = "*"
                        data.Offer_Blacklist = "*"
                        data.Seller_Suppression = "*"
                        data.Explicit_Settlement = "*"
                        data.Backend_buyability = "*"
                        data.bossed_user = "*"
                        data.Shipping_cost = "*"
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')

                        # NEW try
            elif 'noOfferListingsFlag' in o['response']:
                x = newdict['asin']
                y = "Not live"
                newdict = {"asin" : x,"Result" : y}
                url = "http://offerservice-dumper-tools.integ.amazon.com:8000/v2/ajax/source_checker.cgi?website=Amazon.com&domain=prod&realm=USAmazon&mkid=1&method=getOfferListingsForASIN&asin={0}&mid=1&sku={0}&fmid=".format(w)
                url1 = "http://offerservice-dumper-tools.integ.amazon.com:8000/v2/ajax/source_checker_v2.cgi?website=Amazon.com&domain=prod&realm=USAmazon&mkid=1&method=getOfferListingsForASIN&asin={0}&mid=1&sku={0}&fmid=&listing_type=purchasable&discriminator=&condition=Any".format(w)
                y = requests.get(url)
                y1 = requests.get(url1)
                x = y.json()
                x1 = y1.json()
                a = "Item"
                b = (x['response'][0]['highlight'])
                c = "Contribution"
                d = (x['response'][1]['highlight'])
                e = "Price (OLSListing)"
                f = (x['response'][2]['highlight'])
                g = "Price (BuyListing)"
                h = (x['response'][3]['highlight'])
                i = "Xref"
                j = (x['response'][4]['highlight'])
                k = "AvailabilityGpi"
                l = (x['response'][5]['highlight'])
                m = "Seller Suppression"
                n = (x['response'][6]['highlight'])
                o = "Explicit Settlement"
                p = (x['response'][7]['highlight'])
                q = "Offer Blacklist"
                r = (x['response'][8]['highlight'])
                s = "Shipping Cost"
                t = (x['response'][9]['highlight'])
                u = "Backend Buyability"
                v = (x['response'][10]['highlight'])
                try:
                    if x1['offerservice_buyability_checker']['inputs'][1]['sources'][0]['attributes']['blacklist_records'][0]['login']:
                        w1 = (x1['offerservice_buyability_checker']['inputs'][1]['sources'][0]['attributes']['blacklist_records'][0]['login'])
                        w2 = (x1['offerservice_buyability_checker']['inputs'][1]['sources'][0]['attributes']['blacklist_records'][0]['reasonCode'])
                except:
                    w1 = "none"
                    w2 = "none"
                # Sourceability and procurability
                driver.get('https://src-na.corp.amazon.com/getDetailedProcurabilityByIOG?asin={0}&iog=1'.format(newdict['asin']))
                x = driver.find_element_by_xpath("/html/body").text
                ww = str(re.findall(r'"statusReasonCode":"(.*?)"', x)).strip(remove)
                xx = str(re.findall(r'"calculatedStatus":"(.*?)"', x)).strip(remove)

                driver.get('https://src-na.corp.amazon.com/getSourceability?fnsku={asin}&orderingCodes={code}'.format(asin=w,code=vv))
                x = driver.find_element_by_xpath("/html/body").text
                uu = str(re.findall(r'"sourceabilityReason":"(.*?)"', x)).strip(remove)
                vw = str(re.findall(r'"effectiveSourceabilityStatus":"(.*?)"', x)).strip(remove)

                # IPC
                ipc_dict = {}
                driver.get('https://vendorselection-na-iad.iad.proxy.amazon.com/asinSearch?scopeId=AMAZON_US&asin={asin}'.format(asin=w))
                xy = json.loads(driver.find_element_by_xpath("/html/body").text)
                try:
                    # 1 ASIN not found, no planning#####################################*************************************
                    if xy['response']['failure']:
                        ipc_dict = {'asin':w, 'Inventory':'No info on inventory', 'IPCstatus':xy['response']['failure']['failureType'],
                                    'IPCReason':xy['response']['failure']['failureMessage'] ,'Vendorcode':vv,
                                    'Reason':xy['response']['failure']['failureMessage']}
                        print('rule1')
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = w2
                        data.Item = b
                        data.Contribution = d
                        data.Price_OLSListing = f
                        data.Price_BUYListing = h
                        data.Xref = j
                        data.AvailabilityGpi = l
                        data.Offer_Blacklist = r
                        data.Seller_Suppression = n
                        data.Explicit_Settlement = p
                        data.Backend_buyability = v
                        data.bossed_user = w1
                        data.Shipping_cost = t
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')

                    elif xy['exception']:
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = xy['exception']['exceptionType']
                        data.Ipc_status_reason = xy['exception']['exceptionMsg']
                        data.Vendorcode = "*"
                        data.Reason = "*"
                        data.InStock_status = "*"
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = w2
                        data.Item = b
                        data.Contribution = d
                        data.Price_OLSListing = f
                        data.Price_BUYListing = h
                        data.Xref = j
                        data.AvailabilityGpi = l
                        data.Offer_Blacklist = r
                        data.Seller_Suppression = n
                        data.Explicit_Settlement = p
                        data.Backend_buyability = v
                        data.bossed_user = w1
                        data.Shipping_cost = t
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    #2 Planned #####################################False False Planned FC
                    elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSourcingOptionsFromVAR']==False and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSelectedSourcingOptions']==False and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['plannedFcs']:
                        abc = xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors']
                        abccount = len(abc)
                        for a in range(0,abccount):
                            if xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'] , 'IPCstatus':'Planned',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason'] ,'Vendorcode':vv,
                                            'Reason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']}
                            elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'], 'IPCstatus':'Not Planned',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['skippedReasons'] ,'Vendorcode':vv,
                                            'Reason': xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason']}
                        if not ipc_dict:
                            ipc_dict = {'asin':w, 'Inventory':'No info on inventory', 'IPCstatus':'Not Planned',
                                        'IPCReason':'Source vendorcode missing' ,'Vendorcode':vv,
                                        'Reason':'Check Vendor ASIN relations or SC - Rule 2'}
                        else:
                            print('rule2')
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = w2
                        data.Item = b
                        data.Contribution = d
                        data.Price_OLSListing = f
                        data.Price_BUYListing = h
                        data.Xref = j
                        data.AvailabilityGpi = l
                        data.Offer_Blacklist = r
                        data.Seller_Suppression = n
                        data.Explicit_Settlement = p
                        data.Backend_buyability = v
                        data.bossed_user = w1
                        data.Shipping_cost = t
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    #3 NotPlanned #####################################False False No planned FC
                    elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSourcingOptionsFromVAR']==False and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSelectedSourcingOptions']==False and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['plannedFcs']:
                        abc = xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors']
                        abccount = len(abc)
                        for a in range(0,abccount):
                            if xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and  xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'] , 'IPCstatus':'Planned',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason'] ,'Vendorcode':vv,
                                            'Reason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']}

                            elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'], 'IPCstatus':'Not Planned',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['skippedReasons'] ,'Vendorcode':vv,
                                            'Reason':'No planned FCs for this vendorCode - Rule 3'}
                        if not ipc_dict:
                            ipc_dict = {'asin':w, 'Inventory':'No info', 'IPCstatus':'Not Planned',
                                        'IPCReason':'Source vendorcode missing' ,'Vendorcode':vv,
                                        'Reason':'Check Vendor ASIN relations or SC - Rule 3'}
                        else:
                            print('rule3')
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = w2
                        data.Item = b
                        data.Contribution = d
                        data.Price_OLSListing = f
                        data.Price_BUYListing = h
                        data.Xref = j
                        data.AvailabilityGpi = l
                        data.Offer_Blacklist = r
                        data.Seller_Suppression = n
                        data.Explicit_Settlement = p
                        data.Backend_buyability = v
                        data.bossed_user = w1
                        data.Shipping_cost = t
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    #4No sourcing #####################################Flase True no planned FC
                    elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSourcingOptionsFromVAR']==False and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSelectedSourcingOptions']==True and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['plannedFcs']:
                        abc = xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors']
                        abccount = len(abc)
                        for a in range(0,abccount):
                            if xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and  xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'] , 'IPCstatus':'Planned',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason'] ,'Vendorcode':vv,
                                            'Reason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']}

                            elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'], 'IPCstatus':'NO_SOURCING_OPTION',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['skippedReasons'] ,'Vendorcode':vv,
                                            'Reason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason']}
                        if not ipc_dict:
                            ipc_dict = {'asin':w, 'Inventory':'No info', 'IPCstatus':'NO_SOURCING_OPTION',
                                        'IPCReason':'Source vendorcode missing' ,'Vendorcode':vv,
                                        'Reason':' Could not compute vendor TIL: No vendor available for planning for buyingIntent: PREDICTIVE,Check Vendor ASIN relations or SC -Rule 4'}
                        else:
                            print('rule4')
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.bossed_reason = w2
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.Item = b
                        data.Contribution = d
                        data.Price_OLSListing = f
                        data.Price_BUYListing = h
                        data.Xref = j
                        data.AvailabilityGpi = l
                        data.Offer_Blacklist = r
                        data.Seller_Suppression = n
                        data.Explicit_Settlement = p
                        data.Backend_buyability = v
                        data.bossed_user = w1
                        data.Shipping_cost = t
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    #5No sourcing #####################################Flase True  planned FC
                    elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSourcingOptionsFromVAR']==False and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSelectedSourcingOptions']==True and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['plannedFcs']:
                        abc = xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors']
                        abccount = len(abc)
                        for a in range(0,abccount):
                            if xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and  xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'] , 'IPCstatus':'Planned',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason'] ,'Vendorcode':vv,
                                            'Reason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']}

                            elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['vendorCode'] == vv and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['plannedFcs']:
                                ipc_dict = {'asin':w, 'Inventory':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatus'], 'IPCstatus':'NO_SOURCING_OPTION',
                                            'IPCReason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['skippedReasons'] ,'Vendorcode':vv,
                                            'Reason':xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['vendors'][a]['sourcingOptionInStockStatusReason']}
                        if not ipc_dict:
                            ipc_dict = {'asin':w, 'Inventory':'No info on inventory', 'IPCstatus':'NO_SOURCING_OPTION',
                                        'IPCReason':'Source vendorcode missing' ,'Vendorcode':vv,
                                        'Reason':' Could not compute vendor TIL: No vendor available for planning for buyingIntent: PREDICTIVE,Check Vendor ASIN relations or SC -Rule 5'}
                        else:
                            print('rule5')
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = w2
                        data.Item = b
                        data.Contribution = d
                        data.Price_OLSListing = f
                        data.Price_BUYListing = h
                        data.Xref = j
                        data.AvailabilityGpi = l
                        data.Offer_Blacklist = r
                        data.Seller_Suppression = n
                        data.Explicit_Settlement = p
                        data.Backend_buyability = v
                        data.bossed_user = w1
                        data.Shipping_cost = t
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    #6No sourcing #####################################True True  no planned FC*************************************
                    elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSourcingOptionsFromVAR']==True and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSelectedSourcingOptions']==True and not xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['plannedFcs']:
                        ipc_dict = {'asin':w, 'Inventory':'No info on inventory', 'IPCstatus':'NO_SOURCING_OPTION',
                                    'IPCReason':'No vendor available for planning for buyingIntent: PREDICTIVE' ,'Vendorcode':vv,
                                    'Reason':'Check Vendor Asin Relations - Rule 6'}

                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = w2
                        data.Item = b
                        data.Contribution = d
                        data.Price_OLSListing = f
                        data.Price_BUYListing = h
                        data.Xref = j
                        data.AvailabilityGpi = l
                        data.Offer_Blacklist = r
                        data.Seller_Suppression = n
                        data.Explicit_Settlement = p
                        data.Backend_buyability = v
                        data.bossed_user = w1
                        data.Shipping_cost = t
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    #7No sourcing #####################################True True  planned FC*************************************
                    elif xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSourcingOptionsFromVAR']==True and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['noSourcingOptionContext']['noSelectedSourcingOptions']==True and xy['response']['buyingIntentToComputationContext']['PREDICTIVE']['plannedFcs']:
                        ipc_dict = {'asin':w, 'Inventory':'No info on inventory', 'IPCstatus':'NO_SOURCING_OPTION',
                                    'IPCReason':'No vendor available for planning for buyingIntent: PREDICTIVE' ,'Vendorcode':vv,
                                    'Reason':'There are some planned FCs - Rule 7'}

                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = ipc_dict['IPCstatus']
                        data.Ipc_status_reason = ipc_dict['IPCReason']
                        data.Vendorcode = ipc_dict['Vendorcode']
                        data.Reason = ipc_dict['Reason']
                        data.InStock_status = ipc_dict['Inventory']
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = w2
                        data.Item = b
                        data.Contribution = d
                        data.Price_OLSListing = f
                        data.Price_BUYListing = h
                        data.Xref = j
                        data.AvailabilityGpi = l
                        data.Offer_Blacklist = r
                        data.Seller_Suppression = n
                        data.Explicit_Settlement = p
                        data.Backend_buyability = v
                        data.bossed_user = w1
                        data.Shipping_cost = t
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')

                except:
                    if xy['response']['buyingIntentToComputationContext']['IMPORT']:
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = "Import Vendord"
                        data.Ipc_status_reason = "Import Vendord"
                        data.Vendorcode = "Import Vendord"
                        data.Reason = "Import Vendord"
                        data.InStock_status = "Import Vendord"
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = w2
                        data.Item = b
                        data.Contribution = d
                        data.Price_OLSListing = f
                        data.Price_BUYListing = h
                        data.Xref = j
                        data.AvailabilityGpi = l
                        data.Offer_Blacklist = r
                        data.Seller_Suppression = n
                        data.Explicit_Settlement = p
                        data.Backend_buyability = v
                        data.bossed_user = w1
                        data.Shipping_cost = t
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')
                    else:
                        data = db.save(commit=False)
                        data.asin = newdict['asin']
                        data.IPCstatus = "Exception :no response received, check manually"
                        data.Ipc_status_reason = "Exception :no response received, check manually"
                        data.Vendorcode = "Exception :no response received, check manually"
                        data.Reason = "Exception :no response received, check manually"
                        data.InStock_status = "Exception :no response received, check manually"
                        data.sourceability_reason = uu
                        data.sourceability_status = vw
                        data.procurability_status = xx
                        data.procurability_explanation = ww
                        data.buyability_status = newdict['Result']
                        data.bossed_reason = w2
                        data.Item = b
                        data.Contribution = d
                        data.Price_OLSListing = f
                        data.Price_BUYListing = h
                        data.Xref = j
                        data.AvailabilityGpi = l
                        data.Offer_Blacklist = r
                        data.Seller_Suppression = n
                        data.Explicit_Settlement = p
                        data.Backend_buyability = v
                        data.bossed_user = w1
                        data.Shipping_cost = t
                        data.allocatedto = uvw
                        data.pk = None
                        data.runtime = timer
                        data.save()
                        AB_troubleshooting.objects.filter(pk=pk).update(runstatus='complete')

    timerout= timezone.localtime()
    totaltime = timerout - timer
    print(f"I started at {timer} and now completed at {timerout} and total time taken is {totaltime}")
    return render(request, 'new.html')
# ipc_dict = {'asin':w, 'Inventory':'No info on inventory', 'IPCstatus':'Planned - Different code',
                            #                 'IPCReason':'No info' ,'Vendorcode':vv,
                            #                 'Reason':'No info'}
@method_decorator(login_required, name='dispatch')
class Buyablestatus(ListView):
    context_object_name = 'buyable'
    template_name = 'buyablestatus.html'
    model = models.AB_data

    def get_queryset(self):
        current = self.request.user
        date = timezone.localtime()
        return AB_data.objects.filter(allocatedto = current).filter(allocationdate = date)


def kragha1(request):
    db = ABsitestatus()
    timer = timezone.localtime()
    current = request.user
    Sitestatus = AB_troubleshooting.objects.filter(runby=current).values_list('asin','allocatedto')
    with concurrent.futures.ThreadPoolExecutor() as executor:
        num = 1
        total = Sitestatus.count()
        for (asin,allocatedto) in Sitestatus:
            print("currently checking {}, {} out of {}".format(asin,num,total))
            num = num + 1
            url2 = "url".format(asin)
            r = requests.get(url2)
            o = r.json()
            newdict = {"asin" : o['input']['asin'],"Result" :o['response']}
            if 'offerListingList' in o['response']:
                x = newdict['asin']
                y = "Live"
                newdict = {"asin" : x,"Result" : y}
                data = db.save(commit=False)
                data.asin = newdict['asin']
                data.sitestatus = newdict['Result']
                data.allocatedto = allocatedto
                data.pk = None
                data.save()
            elif 'noOfferListingsFlag' in o['response']:
                x = newdict['asin']
                y = "Not live"
                newdict = {"asin" : x,"Result" : y}
                data = db.save(commit=False)
                data.asin = newdict['asin']
                data.sitestatus = newdict['Result']
                data.allocatedto = allocatedto
                data.pk = None
                data.save()

    return render(request,'new.html')

@method_decorator(login_required, name='dispatch')
class Sitestatusall(ListView):
    context_object_name = 'sitestatus'
    template_name = 'sitestatus.html'
    model = models.AB_sitestatus

    def get_queryset(self):
        current = self.request.user
        return AB_sitestatus.objects.filter(allocatedto = current).filter(sitestatus__isnull = False)


def exportsite(request):
    ABoutput1_resource = ABsite()
    current = request.user
    data = AB_sitestatus.objects.all().filter(allocatedto=current)
    dataset = ABoutput1_resource.export(data)
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="@kragha_projects_AB_data.csv"'
    return response
