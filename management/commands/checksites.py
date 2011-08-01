from urllib2 import Request, urlopen, URLError, HTTPError
import datetime
import socket
from django.core.management.base import BaseCommand, CommandError

from websites.models import Website, Incident

timeout = 4
socket.setdefaulttimeout(timeout)

class Command(BaseCommand):
    args = 'none'
    help = 'Performs uptime check of all monitored sites'
    
    
    def handle(self, *args, **options):
        
        site_list = Website.objects.filter(monitor_uptime=True)
        # Simple website availability checker

        for site in site_list:
            site_open = False
            address = str(site.url)
            request = Request(address)
            response_code = -1
            response_text = ''
                        
            try:
                site_open = urlopen(request, timeout=5)
            except HTTPError, e:
                if hasattr(e, 'reason'):
                    response_text = 'We failed to reach a server.\n\nReason: '
                    response_text += str(e.reason)
                elif hasattr(e, 'code'):
                    response_text = 'The server couldn\'t fulfill the request.\n\nError Code:'
                    response_text += str(e.code)
                    response_code = e.code
            except URLError, e:
                if hasattr(e, 'reason'):
                    response_text = 'We failed to reach a server.\n\nReason: '
                    response_text += str(e.reason)
                    #self.stdout.write(response_text)
                elif hasattr(e, 'code'):
                    response_text = 'The server couldn\'t fulfill the request.\n\nError Code:'
                    response_text += str(e.code)
                    response_code = e.code
            
            if(site_open):
                response_code = site_open.getcode()
                  
            if (response_code < 200 or response_code > 203):
                inc = Incident(
                    comment = response_text,
                    error_code = response_code,
                    website = site  
                )
                inc.save()
                site.is_up = False
            else:
                site.is_up = True
                
            site.last_check = datetime.datetime.now()
            site.save()
