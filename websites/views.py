from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import View
from django.contrib.auth import authenticate, get_user_model

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views import View
from .models import Website


User = get_user_model()

# ---------- API Views ----------

@api_view(['POST'])
def register_user(request):
    data = request.data
    if User.objects.filter(email=data['email']).exists():
        return Response({'error': 'User already exists'}, status=400)
    user = User.objects.create_user(username=data['email'], email=data['email'], password=data['password'])
    return Response({'message': 'User created successfully'}, status=201)

@api_view(['POST'])
def login_user(request):
    user = authenticate(username=request.data['email'], password=request.data['password'])
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid Credentials'}, status=401)

class GenerateWebsiteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        business_type = request.data.get('business_type')
        industry = request.data.get('industry')
        content = generate_website_content(business_type, industry)
        website = Website.objects.create(user=request.user, title=f"{business_type} Site", content={'text': content})
        return Response({"id": website.id, "content": content})
    
    
from django.utils.safestring import mark_safe
from django.http import HttpResponse

def preview_website(request, website_id):
    website = get_object_or_404(Website, id=website_id)
    html_content = website.content.get('generated', 'No content available')
    return HttpResponse(mark_safe(html_content))



# ---------- Template Views ----------

class SignupTemplateView(View):
    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('signup')

        user = User.objects.create_user(email=email, username=email, password=password)
        messages.success(request, 'User created successfully. Please log in.')
        return redirect('login')
from django.contrib.auth import authenticate, login

class LoginTemplateView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('dashboard')  # Redirect to home or dashboard
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')
        
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, 'home.html')

from django.utils.decorators import method_decorator
@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        websites = Website.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'dashboard.html', {'websites': websites})
    
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Website
import google.generativeai as genai
import re

# ✅ Configure Gemini with your updated API key
genai.configure(api_key="AIzaSyBLjUBR83y6PfNNI18cTxz4DDSXGrI8Mks")

class CreateWebsiteView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'create_website.html')

    def post(self, request):
        title = request.POST.get('title')
        user_prompt = request.POST.get('content')

        try:
            model = genai.GenerativeModel('models/gemini-1.5-pro')
            prompt = f"Create professional website content with title: '{title}' and description: '{user_prompt}'. Only provide clean HTML code without any explanation or markdown formatting."

            response = model.generate_content(prompt)
            generated_content = response.text.strip()

            # ✅ Clean unwanted parts from the response
            generated_content = re.sub(r'^```html\s*', '', generated_content)  # Remove opening markdown
            generated_content = re.sub(r'```$', '', generated_content)         # Remove closing markdown
            generated_content = re.sub(r'```.*?```', '', generated_content, flags=re.DOTALL)  # Remove any code blocks
            generated_content = re.sub(r'(Key improvements and explanations:|To use this code:).*', '', generated_content, flags=re.DOTALL)

            # Save to database
            Website.objects.create(
                user=request.user,
                title=title,
                content={'generated': generated_content.strip()}
            )

            messages.success(request, 'Website created using Google Gemini AI.')
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f"Error from Gemini: {e}")
            return redirect('create_website')



class EditWebsiteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        website = get_object_or_404(Website, id=pk, user=request.user)
        return render(request, 'edit_website.html', {'website': website})

    def post(self, request, pk):
        website = get_object_or_404(Website, id=pk, user=request.user)
        website.title = request.POST.get('title')
        website.content['text'] = request.POST.get('content')
        website.save()
        messages.success(request, 'Website updated successfully.')
        return redirect('dashboard')


class DeleteWebsiteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        website = get_object_or_404(Website, id=pk, user=request.user)
        website.delete()
        messages.success(request, 'Website deleted successfully.')
        return redirect('dashboard')


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_user(request):
    logout(request)
    return redirect('login')  # Or wherever you want to redirect after logout
