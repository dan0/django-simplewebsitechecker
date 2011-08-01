from django.contrib import admin
from apps.websites.models import *


class ClientNoteAdmin(admin.ModelAdmin):
	prepopulated_fields = { 'slug': ['title'] }
	
class WebsiteNoteAdmin(admin.ModelAdmin):
	prepopulated_fields = { 'slug': ['title'] }
	
class WebsiteNoteInline(admin.TabularInline):
	model = WebsiteNote
	prepopulated_fields = { 'slug': ['title'] }
	
class ClientNoteInline(admin.TabularInline):
	model = ClientNote
	prepopulated_fields = { 'slug': ['title'] }

class IncidentAdmin(admin.ModelAdmin):
	pass
	

class WebsiteAdmin(admin.ModelAdmin):
	prepopulated_fields = { 'slug': ['name'] }
	inlines = [
		WebsiteNoteInline,
	]
	
class SupportTypeAdmin(admin.ModelAdmin):
	prepopulated_fields = { 'slug': ['name'] }



admin.site.register(Website, WebsiteAdmin)
admin.site.register(ClientNote, ClientNoteAdmin)
admin.site.register(WebsiteNote, WebsiteNoteAdmin)
admin.site.register(Incident, IncidentAdmin)
admin.site.register(SupportType, SupportTypeAdmin)

