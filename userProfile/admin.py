from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(UserProfile)

admin.site.register(Categories)
admin.site.register(Project)
admin.site.register(ProjectRatings)
admin.site.register(ProjectPics)
admin.site.register(ProjectTags)
admin.site.register(ProjectReports)
admin.site.register(ProjectDonations)
admin.site.register(ProjectComments)
admin.site.register(FeaturedProject)

