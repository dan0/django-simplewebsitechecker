"""
forms.py

Created by Daniel Drayne on 2010-08-29.
Copyright (c) 2010 Dan Drayne. All rights reserved.
"""
from django.forms import ModelForm
from django.contrib.auth.models import User

from apps.websites.models import *


class SupportForm(ModelForm):
	class Meta:
		model = SupportType
		
		

class WebsiteForm(ModelForm):
	class Meta:
		model = Website
		exclude=('last_check','is_up','slug')

