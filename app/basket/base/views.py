from django.shortcuts import render
from django.template import loader

# Create your views here.
def main(request):
    return render(request, "base/templates/main.html")