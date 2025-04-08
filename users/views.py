# views.py

from django.views import View
from django.shortcuts import render, redirect
import requests

class SignupTemplateView(View):
    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        response = requests.post('http://127.0.0.1:8000/api/register/', data={
            'email': email,
            'password': password,
        })
        if response.status_code == 201:
            return redirect('login')
        else:
            return render(request, 'signup.html', {'error': response.json().get('error')})


class LoginTemplateView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        response = requests.post('http://127.0.0.1:8000/api/login/', data={
            'email': email,
            'password': password,
        })
        if response.status_code == 200:
            tokens = response.json()
            return render(request, 'dashboard.html', {
                'access_token': tokens['access'],
                'refresh_token': tokens['refresh'],
            })
        else:
            return render(request, 'login.html', {'error': response.json().get('error')})


