import datetime

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from websites.extras.utilities import get_favicon, _mkdir


class SupportType(models.Model):
    name = models.CharField(unique=True, max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    
    description = models.TextField(blank=True)
    monthly_hours = models.FloatField()
    monthly_cost = models.FloatField()
    hours_rollover = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Website(models.Model):
    # basic info
    name = models.CharField(unique=True, max_length=250)
    slug = models.SlugField(unique=True, max_length=250)
    url = models.URLField(verify_exists=False)
    owner = models.ForeignKey('tasks.Client')
    
    favicon = models.CharField(blank=True, max_length=120)
    
    # monitoring
    monitor_uptime = models.BooleanField(default=False)
    people_responsible = models.ManyToManyField(User)
    notify_when_down = models.BooleanField(default=True)
    last_check = models.DateTimeField(blank=True, default=datetime.datetime.now)
    is_up = models.BooleanField(default=True)   

    def __unicode__(self):
        return self.name
        
    def save(self, force_insert=False, force_update=False):
        self.slug = slugify(self.name)
        if self.url and not self.favicon:
            favicon_file_path = settings.MEDIA_ROOT + 'client-favicons/' + self.slug
            _mkdir(favicon_file_path)
            favicon_file_path += '/favicon.ico'
            favicon_path = 'client-favicons/' + self.slug + '/favicon.ico'
            
            favicon = get_favicon(self.url, favicon_file_path)
            if favicon:
                self.favicon = favicon_path
            else:
                self.favicon = ''
        
        super(Website, self).save(force_insert, force_update)
        
                
class ClientNote(models.Model):
    create_date = models.DateTimeField(default=datetime.datetime.now)
    title = models.CharField(unique=True, max_length=250)
    slug = models.SlugField(unique=True, max_length=250,unique_for_date="create_date")
    
    content = models.TextField()
    related_to = models.ForeignKey('tasks.Client')
    
    class Meta:
        ordering = ('-create_date', 'title')

    def __unicode__(self):
        return self.title


class WebsiteNote(models.Model):
    create_date = models.DateTimeField(default=datetime.datetime.now,unique_for_date="create_date")
    title = models.CharField(unique=True, max_length=250)
    slug = models.SlugField(unique=True, max_length=250)
    author = models.ForeignKey(User)
    content = models.TextField()
    related_to = models.ForeignKey('Website')

    def __unicode__(self):
        return self.title

        
class Incident(models.Model):
    incident_date = models.DateTimeField(default=datetime.datetime.now)
    error_code = models.CharField(max_length=25)
    error_response = models.CharField(max_length=250)
    website = models.ForeignKey('Website')
    comment = models.TextField()
    
    email_sent = models.BooleanField(default=False, editable=False)

    def save(self, force_insert=False, force_update=False):
        if self.website.monitor_uptime and self.website.notify_when_down:
            
            for user in self.website.people_responsible.all(): 
                if user.email:
                    mail_subject = "Incident: " + self.website.name + " at " + str(self.incident_date)
                    mail_body = "Error code: " + str(self.error_code) + " url:  " + self.website.url 
                    mail_body += "\n\nGo to http://" + Site.objects.get_current().domain + "/sites/" + self.website.slug
                    mail_body += "\n\n" + self.comment
                    send_mail(mail_subject, mail_body, settings.EMAIL_FROM,
                        [user.email], fail_silently=False)
                    self.email_sent = True
                
        super(Incident, self).save(force_insert, force_update)
        
    def __unicode__(self):
        return self.website.name + ": " + str(self.incident_date)       
        

        

        
