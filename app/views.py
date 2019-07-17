from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from app.models import *


def render_claim_verification(request):
    context = {}
    return render(request, 'claim_verification.html', context)
