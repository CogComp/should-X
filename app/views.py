import json

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required

from app.models import *


@login_required
def render_claim_task_list(request):
    username = request.user.username
    session = GoogleQueryAnnotationSession.get_session(username)
    instruction_complete = session.instruction_complete

    finished_batches = json.load(session.finished)
    all_batches = json.load(session.jobs)

    context = {
        "instruction_complete": instruction_complete,
        "finished_batches": finished_batches,
        "all_batches": all_batches
    }

    if len(finished_batches) >= len(all_batches):
        task_id = session.id
    else:
        task_id = -1

    return render(request, 'claim_task_list.html', context)


@login_required
def render_claim_verification(request, batch_id):
    pass

##########################
#        APIs            #
##########################
