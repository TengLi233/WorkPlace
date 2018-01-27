from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm

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
	
	context_dict = {'boldmessage' : 'This tutorial has been put together by Teng Li'}
	return render(request, 'rango/about.html', context=context_dict)
