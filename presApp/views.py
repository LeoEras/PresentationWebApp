from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return HttpResponse("Welcome to the Presentation App!")

def test(request):
        webpages_list = 2
        date_dict = {'access_records': webpages_list}
        return render(request, 'presApp/index.html', context=date_dict)