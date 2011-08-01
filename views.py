import time
import datetime
import urllib

from django.template import RequestContext 
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Count, Sum
from django.utils import simplejson
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from apps.websites.models import *
from apps.websites.forms import *


@login_required
def client_list(request):
    """Returns a list of all clients""" 
    
    clients = []
    for client in Client.objects.all():
        alert = False
        for website in client.website_set.all():
            if website.monitor_uptime and not website.is_up:
                alert = True
        clients.append({'info':client,'alert':alert})
    
    return render_to_response('websites/client_index.html', 
                            { 'client_list': clients },
                            context_instance = RequestContext(request))
                            

@login_required                         
def client_detail(request, client):
    c = Client.objects.filter(slug=client)[:1].annotate(
    total_campaigns=Count('emailcampaign'),
    total_recipients=Sum('emailcampaign__recipients'),
    gross_total=Sum('emailcampaign__gross_amount'),
    total_invoice_amount=Sum('emailcampaign__amount_to_invoice'))
    
    #TODO - urgh, take out ugly shit below and move the _set stuff into the template
    c_detail = []
    c_detail = [{'info': c[0], 
                'campaigns':c[0].emailcampaign_set.all()[:5],
                'notes':c[0].clientnote_set.all()[:5],
                'tasks':c[0].task_set.all(),
                'websites': c[0].website_set.all() }]
    
    updated = False
    if request.method == 'GET': 
        if request.GET.get('updated'):
            updated = True
    
    return render_to_response('websites/client_detail.html', 
                            { 'client': c_detail[0], 'updated': updated },
                            context_instance = RequestContext(request))

    datestring = '01'+month+year
    this_month = time.strptime(datestring,"%d%m%Y")
    this_month = datetime.datetime.fromtimestamp(time.mktime(this_month))


@login_required
def client_edit(request, client):

    a = Client.objects.get(slug=client)

    if request.method == 'POST':
        f = ClientForm(request.POST, instance=a)
        if f.is_valid():
            f.save()
            return HttpResponseRedirect('/clients/'+a.slug+"/?updated=1")
    else:
        f = ClientForm(instance=a)
    return render_to_response('websites/client_edit.html', 
                            { 'clientform': f },
                            context_instance = RequestContext(request))


@login_required
def support_index(request):
    """Returns a list of all Support Types"""   

    return render_to_response('websites/support_index.html', 
                            { 'support_list': SupportType.objects.all() },
                            context_instance = RequestContext(request))


@login_required
def website_list(request):
    """Returns a list of all Websites"""
    
    users = User.objects.exclude(username='root').exclude(username='admin')
    return render_to_response('websites/website_index.html', 
                            { 'users':users,'site_list': Website.objects.all().extra(
                            select={'lower_name': 'lower(name)'}).order_by('is_up','lower_name')},
                            context_instance = RequestContext(request))
                            

@login_required
def website_add(request):
    if request.method == 'POST':
        f = WebsiteForm(request.POST)
        if f.is_valid():
            new_website = f.save()
            return HttpResponseRedirect("/sites/?added")
    else:
        f = WebsiteForm()

    return render_to_response('websites/website_add.html', 
                            { 'websiteform': f },
                            context_instance = RequestContext(request))
                            

@login_required
def website_edit(request, website):

    w = Website.objects.get(id=website)

    if request.method == 'POST':
        f = WebsiteForm(request.POST, instance=w)
        if f.is_valid():
            f.save()
            return HttpResponseRedirect('/sites/?updated')
    else:
        f = WebsiteForm(instance=w)

    return render_to_response('websites/website_edit.html', 
                            { 'websiteform': f },
                            context_instance = RequestContext(request))
                            

@login_required                         
def website_detail(request, website):
    """displays info on one website"""
    status = 'down'
    w = Website.objects.get(id=website)
    if(w.is_up):
        status = 'up'
    return render_to_response('websites/website_detail.html', 
                            { 'status':status,'site': w },
                            context_instance = RequestContext(request)) 
    

@login_required                     
def website_check(request, website):
    
    response = {}
    status = ''
    message = ''
    site = Website.objects.get(id=website)
    address = str(site.url)
    testcode = None
    try:
        testcode = urllib.urlopen(address).getcode()
    except IOError:
        message = 'Cannot open site. DNS error?' # TODO - log, maybe.  
        testcode = -1
    if (testcode != 200):
        inc = Incident(
            error_code = testcode,
            website = site  
        )
        inc.save()
        site.is_up = False
        message = 'Site error reported, incident logged'
        
        #TODO - this shit should be part of saving an incident, and cleaner
        phone_number = False
        try:
            phone_number = site.person_responsible.get_profile().phone_number
        except ObjectDoesNotExist:
            print site.person_responsible.username + " has no phone number" #todo Log
            
        if phone_number:
            from extras import txtlocal
            sms = 'Error in site: ' + site.name +' - last check at '+ str(datetime.datetime.now())
            txtlocal.sendSMS(phone_number,sms)   
            
    else:
        site.is_up = True
        message = "All good"
    
    site.last_check = datetime.datetime.now()
    site.save()
    
    response.update({'code':testcode,'message':message,'checkedon':str(site.last_check)})
    return HttpResponse(simplejson.dumps(response),mimetype='application/json')


@login_required                         
def client_add(request):
    s = False
    if request.method == 'POST':
        f = ClientForm(request.POST)
        if f.is_valid():
            new_client = f.save()

            return HttpResponseRedirect("/clients/?updated=1")
    else:
        f = ClientForm()

    return render_to_response('websites/client_add.html', 
                            { 'clientform': f, 'supporttype': s },
                            context_instance = RequestContext(request))
                

@login_required                         
def support_detail(request, supporttype):
    """Returns details of an individual support type"""

    updated = False
    if request.method == 'GET': 
        if request.GET.get('updated'):
            updated = True
    
    s = SupportType.objects.get(slug=supporttype)
    
    return render_to_response('websites/support_detail.html', 
                            { 'supporttype': s, 'updated':updated },
                            context_instance = RequestContext(request))
            

@login_required         
def support_edit(request, supporttype):

    s = SupportType.objects.get(slug=supporttype)

    if request.method == 'POST':
        f = SupportForm(request.POST, instance=s)
        if f.is_valid():
            f.save()
            return HttpResponseRedirect('/support/'+s.slug+"/?updated=1")
    else:
        f = SupportForm(instance=s)

    return render_to_response('websites/support_edit.html', 
                            { 'supportform': f, 'supporttype': s },
                            context_instance = RequestContext(request))


@login_required         
def support_add(request):
    s = False
    if request.method == 'POST':
        f = SupportForm(request.POST)
        if f.is_valid():
            new_supporttype = f.save()
            return HttpResponseRedirect("/support/?updated=1")
    else:
        f = SupportForm()

    return render_to_response('websites/support_add.html', 
                            { 'supportform': f, 'supporttype': s },
                            context_instance = RequestContext(request))
                            

@login_required
def tasks_for_user(request):
    tl = Task.objects.filter(person_responsible=request.user)
    
    return render_to_response('websites/tasks_user.html', 
                            { 'task_list': tl },
                            context_instance = RequestContext(request))
                            

@login_required                         
def task_add(request):
    if request.method == 'POST':
        f = TaskForm(request.POST)
        if f.is_valid():
            new_tasktype = f.save()
            return HttpResponseRedirect("/tasks/?updated=1")
    else:
        f = TaskForm()

    return render_to_response('websites/task_add.html', 
                            { 'taskform': f},
                            context_instance = RequestContext(request))
                            

@login_required
def task_edit(request, taskid):

    t = Task.objects.get(id=taskid)

    if request.method == 'POST':
        f = TaskForm(request.POST, instance=t)
        if f.is_valid():
            f.save()
            return HttpResponseRedirect('/tasks/'+t.id+"/?updated=1")
    else:
        f = TaskForm(instance=t)

    return render_to_response('websites/support_edit.html', 
                            { 'supportform': f, 'task': t },
                            context_instance = RequestContext(request))


@login_required
def user_list(request):
    """Returns a list of all users"""

    return render_to_response('websites/user_index.html', 
                            { 'user_list': User.objects.all().order_by('username') },
                            context_instance = RequestContext(request))


@login_required
def user_add(request):
    if request.method == 'POST':
        uform = UserForm(request.POST)
        pform = UserProfileForm(request.POST)
        
        if uform.is_valid() and uform.is_valid():
            new_user = uform.save()
            new_user.set_password(new_user.password)
            new_user.save()
            new_profile = pform.save(commit = False)
            new_profile.user = new_user
            new_profile.save()
            return HttpResponseRedirect("/users/?updated=1")
    else:
        uform = UserForm()
        pform = UserProfileForm()
    return render_to_response('websites/user_add.html', 
                            { 'uform': uform,'pform':pform},
                            context_instance = RequestContext(request))
                            
                            
@login_required         
def user_edit(request, userid):

    user = User.objects.get(id=userid)
    try:
        profile = UserProfile.objects.get(user=user)
    except ObjectDoesNotExist:
        profile = UserProfile(user=user)
        
    if request.method == 'POST':
        uform = UserForm(request.POST, instance=user)
        pform = UserProfileForm(request.POST, instance=profile)
        
        if uform.is_valid() and uform.is_valid():
            uform.save()
            pform.save()
            return HttpResponseRedirect("/users/?updated=1")
    else:
        uform = UserForm(instance=user)
        pform = UserProfileForm(instance=profile)

    return render_to_response('websites/user_edit.html', 
                            { 'uform': uform,'pform':pform},
                            context_instance = RequestContext(request))


@login_required
def dashboard(request):

    """docstring for dashboard"""
    return render_to_response('websites/dashboard.html',
                        context_instance = RequestContext(request))
