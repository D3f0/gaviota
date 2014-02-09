#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect

def user_login(request):
    if request.method == 'POST':
        
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return render_to_response('login.html', {
                                            'error': 'La cuenta %s se encuentra deshabilitada.' % username
                                                         }, 
                                  context_instance=RequestContext(request))
                
        else:
            return render_to_response('login.html', {
                                            'error': 'Nombre de usuario o contraseña incorrectas.' 
                                                         }, 
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('login.html', {}, 
                                  context_instance=RequestContext(request))

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')