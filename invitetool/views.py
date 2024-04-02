from django.shortcuts import redirect

def redirect_gui(request):
    response = redirect('gui/')
    return response