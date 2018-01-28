from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from rango.models import Category
from rango.models import Page, UserProfile
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm

def add_category(request):
	form = CategoryForm()

	# A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			return index(request)

		else:
			print(form.errors)

	return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None

	form = PageForm()
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request, category_name_slug)
			else:
				print(form.errors)
	context_dict = {'form': form, 'category': category}
	return render(request, 'rango/add_page.html', context_dict)

def show_category(request, category_name_slug):
	context_dic = {}

	try:
		category = Category.objects.get(slug=category_name_slug)
		pages = Page.objects.filter(category=category)
		context_dic['pages'] = pages
		context_dic['category'] = category
	except Category.DoesNotExist:
		context_dic['pages'] = None
		context_dic['category'] = None

	return render(request, 'rango/category.html', context_dic)

def index(request):
    #return HttpResponse("Rango says hey there partner!<br/><a href='/rango/about/'>About</a>")
	
	#Construct a dictionary to pass to the template engin as its context
	#Note the key boldmessage is the same as {{boldmessage}} in the template!

	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]

	context_dict = {'categories' : category_list,
					'pages': page_list}
	
	# Return a rendered response to send to the client
	# We make use of the shortcut function to make our lives easier
	# Note that the first parameter is the template we wish to use
	return render(request, 'rango/index.html', context_dict)
def about(request):
    #return HttpResponse("Rango says here is the about page.<br/><a href='/rango/about/'>Index</a>")
	return render(request, 'rango/about.html')

def register(request):
	registered = False
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()
			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			profile.save()
			registered = True
		else:
			print(user_form.errors, profile_form.errors)
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request, 'rango/register.html',
				  {
					  'user_form': user_form,
					  'profile_form': profile_form,
					  'registered': registered
				  })

def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('index'))
			else:
				return HttpResponse("Your Rango account is disabled.")
		else:
			print("Invalid login details: {0}, {1}".format(username, password))
			return HttpResponse("Invalid login details supplied.")
	else:
		return render(request, 'rango/user_login.html', {})

@login_required
def restricted(request):
    context_dict = {'boldmessage': "Since you're logged in, you can see this text!"}
    return render(request, 'rango/restricted.html', context_dict)

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))