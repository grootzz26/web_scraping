import time

from django.shortcuts import render
from django.http import HttpResponse
from .forms import *
from root.settings import web_url
from .task import *
# Create your views here.


def temp_view(request):
    if request.method == 'POST':
        form = AsinForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            start = time.perf_counter()
            result =  bulk_download(request, web_url, data)
            end = time.perf_counter()
            print("#############--------:::", end-start)
    else:
        form = AsinForm()
    return render(request, "index.html", {'form':form})
