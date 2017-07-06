from django.contrib import admin
from polls.models import Poll,Choice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    fieldsets = [
        (None,                      {'fields': ['question']}),
        ('Information sur la date', {'fields': ['pub_date'], 'classes':['collapse']}),
    ]
    inlines = [ChoiceInline]
    search_fields = ['question']
    date_hierarchy = 'pub_date'

admin.site.register(Poll, PollAdmin)
admin.site.register(Choice)