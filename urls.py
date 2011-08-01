from django.conf.urls.defaults import *
from apps.websites.models import *


urlpatterns = patterns('',
	#(r'^(?P<year>\d{4})/(?P<month>\d{2})/$','archive_month', campaign_info_dict, 
	#    'campaignmonitordash_savedcampaign_archive_month'),
	(r'^support/add','apps.websites.views.support_add'),
	(r'^support/(?P<supporttype>.*)/edit','apps.websites.views.support_edit'),
	(r'^support/(?P<supporttype>.*)/','apps.websites.views.support_detail'),
	(r'^support/','apps.websites.views.support_index'),
	(r'^add','apps.websites.views.website_add'),
	(r'^(?P<website>.*)/edit','apps.websites.views.website_edit'),
	(r'^(?P<website>.*)/check','apps.websites.views.website_check'),
	(r'^(?P<website>.*)/','apps.websites.views.website_detail'),
	(r'^','apps.websites.views.website_list'),
)

