from django.contrib import admin


class CustodyImportationRowAdmin(admin.ModelAdmin):
    list_display = ('id', 'importation', 'row', 'days_attended', 'surnames')
    list_per_page = 25
