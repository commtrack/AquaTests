from django.http import HttpResponse
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.exceptions import *
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.utils.translation import ugettext_lazy as _
from django.db.models.query_utils import Q
from django.core.urlresolvers import reverse

from datetime import timedelta
from django.db import transaction
import uuid

from models import *
from django.contrib.auth.models import User 

#from forms import *
import logging
import hashlib
import settings
import traceback
import sys
import os
import string
import submitprocessor


#@login_required()
def show_submits(request, template_name="receiver/show_submits.html"):    
    context = {}
    slogs = Submission.objects.all()
    context['submission_items'] = slogs    
    return render_to_response(template_name, context, context_instance=RequestContext(request))


#@login_required()    
def single_submission(request, submission_id, template_name="receiver/single_submission.html"):
    context = {}        
    slog = Submission.objects.all().filter(id=submission_id)
    context['submission_item'] = slog[0]    
    rawstring = str(slog[0].raw_header)
    rawstring = rawstring.replace(': <',': "<')
    rawstring = rawstring.replace('>,','>",')
    processed_header = eval(rawstring)
    
    get_original = False
    for item in request.GET.items():
        if item[0] == 'get_original':
            get_original = True           
    
    if get_original:
        response = HttpResponse(mimetype='text/plain')
        fin = open(slog[0].raw_post ,'r')
        txt = fin.read()
        fin.close()
        response.write(txt) 
        return response
    
    attachments = Attachment.objects.all().filter(submission=slog[0])
    context ['processed_header'] = processed_header
    context['attachments'] = attachments
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def raw_submit(request, template_name="receiver/submit.html"):
    context = {}            
    logging.debug("begin raw_submit()")
    if request.method == 'POST':
        new_submission = submitprocessor.do_raw_submission(request.META,request.raw_post_data)        
        if new_submission == '[error]':
            template_name="receiver/submit_failed.html"            
        else:
            context['transaction_id'] = new_submission.transaction_uuid
            context['submission'] = new_submission
            attachments = Attachment.objects.all().filter(submission=new_submission)            
            context['attachments'] = attachments            
            template_name="receiver/submit_complete.html"
            
    #for real submissions from phone, the content-type should be:
    #mimetype='text/plain' # add that to the end fo the render_to_response()                                     
    return render_to_response(template_name, context, context_instance=RequestContext(request))


def backup(request, template_name="receiver/backup.html"):
#return ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
    context = {}            
    logging.debug("begin backup()")
    if request.method == 'POST':
        new_submission = submitprocessor.do_raw_submission(request.META,request.raw_post_data)        
        if new_submission == '[error]':
            template_name="receiver/submit_failed.html"            
        else:
            #todo: get password presumably from the HTTP header            
            new_backup = Backup(submission=new_submission, password='password')
            new_backup.save()
            response = HttpResponse(mimetype='text/plain')          
                                      
            context['backup_id'] = new_backup.backup_code                        
            template_name="receiver/backup_complete.html"            
            from django.template.loader import render_to_string
            rendering = render_to_string('receiver/backup_complete.html', { 'backup_id': new_backup.backup_code })
            
            response.write(rendering)
            response['Content-length'] = len(rendering)
            return response                                         
            
    return render_to_response(template_name, context, context_instance=RequestContext(request),mimetype='text/plain')


def restore(request, code_id, template_name="receiver/restore.html"):
    context = {}            
    logging.debug("begin restore()")
    #need to somehow validate password, presmuably via the header objects.
    restore = Backup.objects.all().filter(backup_code=code_id)
    if len(restore) != 1:
        template_name="receiver/nobackup.html"
        return render_to_response(template_name, context, context_instance=RequestContext(request),mimetype='text/plain')
    original_submission = restore[0].submission
    attaches = Attachment.objects.all().filter(submission=original_submission)
    for attach in attaches:
        if attach.attachment_content_type == "text/xml":
            response = HttpResponse(mimetype='text/xml')
            fin = open(attach.filepath,'r')
            txt = fin.read()
            fin.close()
            response.write(txt)
            
            verify_checksum = hashlib.md5(txt).hexdigest()
            if verify_checksum == attach.checksum:                
                return response
            else:               
                continue
    
    template_name="receiver/nobackup.html"
    return render_to_response(template_name, context, context_instance=RequestContext(request),mimetype='text/plain')
        
                           
                      
    