import urllib
import datetime

from clientdb.models import Website, Incident


site_list = Website.objects.filter(monitor_uptime=True)

# Simple website availability checker

for site in site_list:
	address = str(site.url)
	print address
	testcode = None
	message = ""
	try:
		testcode = urllib.urlopen(address).getcode()
	except IOError:
		print "cannot open site. DNS error?" # TODO - should I log as incidents?
		testcode = -1
	
	if (testcode != 200):
		inc = Incident(
			error_code = testcode,
			website = site,
			comment = message
		)
		inc.save()
		
		site.is_up = False
	else:
		site.is_up = True
	
	site.last_check = datetime.datetime.now()
	site.save()