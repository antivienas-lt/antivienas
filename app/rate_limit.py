from ipware import get_client_ip
from django.shortcuts import render

def ip_key(group, request):
    ip, _ = get_client_ip(request)
    return ip

def ratelimited_error(request, exception):
    return render(request, 'ratelimited.html', status=429)