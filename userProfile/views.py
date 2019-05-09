from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from .forms import UpdateProfile,UpdateUser

from .forms import ProjectForm, ProjectPicsForm, ProjectTagsForm
from .forms import UserForm, UserProfileInfoForm, MakeDonationForm, AddCommentForm, ReportProjectForm, RateProjectForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .models import *
from django.db.models import Sum, Avg
from django.shortcuts import redirect


def index(request):
    last_projects = Project.objects.all().order_by('start_date')[:5]
    rated_projects = Project.objects.filter(ratings__isnull=False).order_by('-ratings__average')[:5]
    latest_projects = []
    for project in last_projects:
        latest_projects.append(add_project_details(project))
    categories = Categories.objects.all
    admin_featured_projects = FeaturedProject.objects.all()[:5]
    featured_projects = []
    # for project in admin_featured_projects:
        # featured_projects.append(add_project_details(project))
    return render(request, 'userProfile/index.html', {'latest_projects': latest_projects,
                                                      'categories': categories,
                                                      'featured_projects': admin_featured_projects,
                                                      'rated_projects': rated_projects,
                                                      })


@login_required
def special(request):
    return HttpResponse("You are logged in !")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'profile_pic' in request.FILES:
                print('found it')
                profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            user.is_active = False
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('userProfile/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = user_form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
             #registered = True
            user.is_active = False
            user.save()
            return render(request, 'userProfile/mail_confirmation.html', {})

        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request, 'userProfile/registeration.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})
 
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            username = User.objects.get(email=email)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            username = None

        if username is not None:
           user = authenticate(username=username, password=password)
           if user:
              if user.is_active:
                 login(request, user)
                 return HttpResponseRedirect(reverse('index'))
              else:
                 return render(request, 'userProfile/invalid_login.html', {})
           else:
               return render(request, 'userProfile/invalid_login.html', {})
        else:
            print("Someone tried to login and failed.")
            print("They used email: {} and password: {}".format(email, password))
            return render(request, 'userProfile/invalid_login.html', {})
    else:
        return render(request, 'userProfile/login.html', {})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        #user.is_active = True
        # return HttpResponseRedirect(reverse('index'))
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')



#create new project
@login_required
def create_project(request):
    if request.method == 'POST':
        print(request.user.id)
        project_form = ProjectForm(data=request.POST)
        project_pics_form = ProjectPicsForm(data=request.POST)
        project_tags_form = ProjectTagsForm(data=request.POST)
        if project_form.is_valid() and project_pics_form.is_valid() and project_tags_form.is_valid():
            project = project_form.save(commit=False)
            current_user = User.objects.get(id=request.user.id)
            # print(type(current_user))
            current_user_profile = UserProfile.objects.filter(user=current_user)
            # print(type(current_user_profile.first()))
            project.user = current_user_profile.first()
            project.save()
            if 'project_pictures' in request.FILES and request.FILES['project_pictures'] is not None:
                print(request.FILES.getlist('project_pictures')[0])
                for img in request.FILES.getlist('project_pictures'):
                    project_pic = ProjectPics()
                    project_pic.project = project
                    project_pic.project_picture = img
                    project_pic.save()
            project_tags = project_tags_form.save(commit=False)
            if 'project_tag' in request.POST and request.POST['project_tag'] is not "":
                project_tags.project = project
                project_tags.save()
            return redirect('/'+current_user.username+'/projects/', request=request)
            # return render(request, 'userProfile/create_project.html', {
            #     'project_form': project_form,
            #     'project_pics_form': project_pics_form,
            #     'project_tags_form': project_tags_form,
            #     'errors': None
            # })
        else:
            return render(request, 'userProfile/create_project.html', {
                'project_form': project_form,
                'errors': [project_form.errors, project_pics_form.errors, project_tags_form.errors]
            })
    else:
        project_form = ProjectForm()
        project_pics_form = ProjectPicsForm()
        project_tags_form = ProjectTagsForm()
    return render(request, 'userProfile/create_project.html', {
        'project_form': project_form,
        'project_pics_form': project_pics_form,
        'project_tags_form': project_tags_form,
        'errors': None
    })


# Show all projects
@login_required
def show_projects(request):
    projects = Project.objects.all()
    projectDetails = []
    for project in projects:
        projectDetails.append(add_project_details(project))
    return render(request, 'project/index.html', {'projects': projectDetails})


# @login_required
# def get_donation_form(request, project, current_user_profile):
#     if request.method == 'POST':
#         donation_form = MakeDonationForm(data=request.POST)
#         if donation_form.is_valid():
#             donation = donation_form.save(commit=False)
#             donation.project = project
#             donation.user = current_user_profile.first()
#             donation.save()
#             return MakeDonationForm()
#     else:
#         donation_form = MakeDonationForm()
#     return donation_form


# @login_required
# def get_comment_form(request, project, current_user_profile):
#     if request.method == 'POST':
#         comment_form = AddCommentForm(data=request.POST)
#         if comment_form.is_valid():
#             comment = comment_form.save(commit=False)
#             comment.project = project
#             comment.user = current_user_profile.first()
#             comment.save()
#             return AddCommentForm()
#     else:
#         comment_form = AddCommentForm()
#     return comment_form


# @login_required
# def get_report_form(request, project, current_user_profile):
#     if request.method == 'POST':
#         report_form = ReportProjectForm(data=request.POST)
#         if report_form.is_valid():
#             report = report_form.save(commit=False)
#             report.project = project
#             report.user = current_user_profile.first()
#             report.save()
#             return ReportProjectForm()
#     else:
#         report_form= ReportProjectForm()
#     return report_form


# @login_required
# def get_rating_form(request, project, current_user_profile):
#     if request.method == 'POST':
#         rating_form = RateProjectForm(data=request.POST)
#         if rating_form.is_valid():
#             rate = rating_form.save(commit=False)
#             rate.project = project
#             rate.user = current_user_profile.first()
#             rate.save()
#             return RateProjectForm()
#     else:
#         rating_form = RateProjectForm()
#     return rating_form

# show a single project
@login_required
def show_a_project(request, id):
    project = get_object_or_404(Project, pk=id)
    project_details = add_project_details(project)
    current_user = User.objects.get(id=request.user.id)
    current_user_profile = UserProfile.objects.filter(user=current_user)

    if request.method == 'POST':
        donation_form = MakeDonationForm(data=request.POST)
        if donation_form.is_valid():
            donation = donation_form.save(commit=False)
            donation.project = project
            donation.user = current_user_profile.first()
            donation.save()
            donation_form = MakeDonationForm()
            return HttpResponseRedirect(reverse('show_project', args=[id]))
        comment_form = AddCommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.project = project
            comment.user = current_user_profile.first()
            comment.save()
            return HttpResponseRedirect(reverse('show_project', args=[id]))
        report_form = ReportProjectForm(data=request.POST)
        if report_form.is_valid():
            report = report_form.save(commit=False)
            report.project = project
            report.user = current_user_profile.first()
            report.save()
            return HttpResponseRedirect(reverse('show_project', args=[id]))
        rating_form = RateProjectForm(data=request.POST)
        if rating_form.is_valid():
            rate = rating_form.save(commit=False)
            rate.project = project
            rate.user = current_user_profile.first()
            rate.save()
            report.save()
            return HttpResponseRedirect(reverse('show_project', args=[id]))
    else:
        donation_form = MakeDonationForm()
        comment_form = AddCommentForm()
        report_form = ReportProjectForm()
        rating_form= RateProjectForm()
    return render(request, 'project/project.html', {
        'project': project_details,
        'project1': project,
        'donation_form': donation_form,
        'comment_form': comment_form,
        'report_form': report_form,
        'rate_project': rating_form
    })

# # show a single project
# @login_required
# def show_a_project(request, id):
#     project_details = show_a_project_details(request, id)
#     current_user = User.objects.get(id=request.user.id)
#     current_user_profile = UserProfile.objects.filter(user=current_user)
#     donation_form = get_donation_form(request, project_details[0], current_user_profile)
#     comment_form = get_comment_form(request, project_details[0], current_user_profile)
#     report_form = get_report_form(request, project_details[0], current_user_profile)
#     rating_form = get_rating_form(request, project_details[0], current_user_profile)
#     return render(request, 'project/project.html', {
#         'project': project_details[0],
#         'donation_form': donation_form,
#         'comment_form': comment_form,
#         'report_form': report_form,
#         'comments': project_details[1],
#         'pictures': project_details[3],
#         'total_donation': project_details[3],
#         'rate_project': rating_form,
#         'average_rating': project_details[4]
#     })
#         return HttpResponseRedirect(reverse('show_project', args=[id]))

# show user's projects
@login_required
def get_projects(request, username):
    user = User.objects.get(username=username)
    userprofile = UserProfile.objects.get(user=user)
    projects = userprofile.project_set.all()
    donations = userprofile.projectdonations_set.all()
    projectDetails = []
    for project in projects:
        projectDetails.append(add_project_details(project))
    return render(request, 'userProfile/projects.html', {'projects': projectDetails,
                                                         'donations': donations,
                                                         })


def add_project_details(project):
    # to access project pics
    # project.projectpics_set.all()
    projectInfo = ProjectDetail(project.id, project.user.id, project.category.id, project.title, project.details,
                      project.start_date, project.end_date, project.total_target,
                      ProjectDonations.objects.filter(project=project).aggregate(Sum("donation_amount")),
                      ProjectRatings.objects.filter(project=project).aggregate(Avg("user_rating")))
    return projectInfo

# get user's donations
@login_required
def get_user_donations(request, username):
    user = User.objects.get(username=username)
    userprofile = UserProfile.objects.get(user=user)
    donations = userprofile.projectdonations_set.all()
    return render(request, 'userProfile/donations.html', {'donations': donations})

# get category's project
@login_required
def get_category_projects(request,id):
    category = get_object_or_404(Categories, pk=id)
    projects = category.project_set.all()
    projectDetails = []
    for project in projects:
        projectDetails.append(add_project_details(project))
    return render(request, 'Category/projects.html', {'category':category,'projects': projectDetails})


def get_user_profile(request, username):
    user = User.objects.get(username=username)
    userprofile = UserProfile.objects.get(user=user)
    return render(request, 'userProfile/user_profile.html', {"user":user, "userprofile":userprofile})



def update_user_profile(request, username):
    user = User.objects.get(username=username)
    userprofile = UserProfile.objects.get(user=user)
    if request.method == 'POST':
        profileform = UpdateProfile(data=request.POST, files=request.FILES, instance=request.user.userprofile, initial={'phone': userprofile.phone, 'country': userprofile.country,
                                                                                                'lastname': userprofile.lastname,
                                                                                                'firstname': userprofile.firstname,
                                                                                                'birthday': userprofile.birthday, 'profile_pic': userprofile.profile_pic})
        userform = UpdateUser(data=request.POST, instance=request.user, initial={'username': user.username, 'email': user.email})

        if userform.is_valid() and profileform.is_valid():
            updatedprofile = profileform.save(commit=False)
            if 'profile_pic' in request.FILES:
                updatedprofile.profile_pic = request.FILES['profile_pic']
            updatedprofile.save()
            return render(request, 'userProfile/index.html', {"user": user, "userprofile": userprofile})
    else:
        profileform = UpdateProfile(instance=request.user.userprofile, initial={'phone': userprofile.phone, 'country': userprofile.country,
                                             'lastname': userprofile.lastname,
                                             'firstname': userprofile.firstname,
                                             'birthday': userprofile.birthday, 'profile_pic': userprofile.profile_pic})
        userform = UpdateUser( instance=request.user, initial={'username': user.username, 'email': user.email})
    context = {
        "userform": userform,
        "profileform": profileform}
    return render(request, 'userProfile/update_user_profile.html', context)


def delete_user_profile(request, username):
    user = User.objects.get(username=username)
    userprofile = UserProfile.objects.get(user=user)
    logout(request)
    try:
      projects = Project.objects.get(user=userprofile)
    except(TypeError, ValueError, OverflowError, Project.DoesNotExist):
      projects = None

    if projects is not None:
        projects.delete()

    userprofile.delete()
    user.delete()
    return HttpResponseRedirect(reverse('index'))


def search(request,data):
    title_matched= Project.objects.filter(title__icontains=data)
    details_matched = Project.objects.filter(details__icontains=data)
    tags=ProjectTags.objects.filter(project_tag__icontains=data)
    projects = []
    for tag in tags:
        taged_matched = tag.project
        projects.append(add_project_details(taged_matched))
    for project in title_matched:
        projects.append(add_project_details(project))
    for project in details_matched:
        projects.append(add_project_details(project))
    return render(request, 'project/search.html', {'projects': projects})





class ProjectDetail(Project):
    def __init__(self, projectId, user, category, title, details, start_date, end_date, total_target, total_donations,
                 average_rating):
        Project.__init__(self, projectId, user, category, title, details, start_date, end_date, total_target)
        self.total_donations = 0 if total_donations['donation_amount__sum'] is None else float(total_donations['donation_amount__sum'])
        self.average_rating = average_rating['user_rating__avg']
        self.percentage = "{0:.2f}".format((self.total_donations/total_target)*100)


def delete_user_project(request, id):
    project = get_object_or_404(Project, pk=id)
    project_details = add_project_details(project)
    current_user = User.objects.get(id=request.user.id)
    current_user_profile = UserProfile.objects.filter(user=current_user)
    donation = ProjectDonations.objects.filter(project=project).aggregate(Sum("donation_amount"))
    print("They used totaldonations: {} ".format(donation['donation_amount__sum']))
    if donation['donation_amount__sum'] == None:
        project.delete()
        return HttpResponseRedirect(reverse('index'))
    else:
      if float(donation['donation_amount__sum']) < .25*project.total_target:
          project.delete()
          return HttpResponseRedirect(reverse('index'))
      else:
          print("They used totaldonations: {} ".format( donation['donation_amount__sum']))
          return render(request, 'userProfile/delete_project_err.html')
