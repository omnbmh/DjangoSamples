#from django.http import HttpResponse
from django.shortcuts import render

def hello(request):
    #return HttpResponse("Hello Wolrd !")
    context = {}
    context['hello'] = 'HelloWorld from Templates !'
    return render(request,'hello.html',context)
