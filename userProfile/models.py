from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from star_ratings.models import Rating

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(default='user', null=True, max_length=20)
    lastname = models.CharField(default='user', null=True, max_length=20)
    phone = models.BigIntegerField(default='01000000000', null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, default='profile_pics/avatar.png', null=True)
    birthday = models.DateField(default=timezone.now, null=True)
    portfolio_site = models.URLField(default='http://www.facebook.com', null=True, blank=True)
    country = models.CharField(default='Egypt', null=True, max_length=20)


    def __str__(self):
        return self.user.email


class Categories(models.Model):
    category = models.CharField(max_length=15, null=True, unique=True)

    def __str__(self):
        return self.category


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=50, default='Project Title', unique=True)
    details = models.TextField(max_length=300, null=True)
    start_date = models.DateField(default=timezone.now, null=True)
    end_date = models.DateField(default=timezone.now, null=True)
    total_target = models.BigIntegerField(default=10, null=True)
    ratings = GenericRelation(Rating, related_query_name='project')

    # def __init__(self, id, user, category, title, details, start_date, end_date, total_target):
    #     super(Project, self).__init__()
    #     self.id = id
    #     self.user = UserProfile.objects.get(pk=user)
    #     self.category = Categories.objects.get(pk=category)
    #     self.title = title
    #     self.details = details
    #     self.start_date = start_date
    #     self.end_date = end_date
    #     self.total_target = total_target

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title


class ProjectPics(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    project_picture = models.ImageField(upload_to='images/', null=True)


class ProjectTags(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    project_tag = models.CharField(max_length=50, null=True)


class ProjectReports(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    report_body = models.TextField(max_length=250, null=True)


class ProjectRatings(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    user_rating = models.IntegerField(default='0', null=True)


class ProjectComments(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    comment_body = models.TextField(max_length=250, null=True)
    comment_reports = models.IntegerField(default=0, null=True)


class ProjectDonations(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    donation_amount = models.BigIntegerField(default=0, null=True)


class FeaturedProject(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.project.title
