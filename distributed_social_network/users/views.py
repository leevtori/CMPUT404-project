from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, HttpResponse

User = get_user_model()

# Create your views here.
def index(request):
    return render(request, "login.html", {})

def login_view(request):
    username = request.POST.get('username', False)
    password = request.POST.get('password', False)
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse("You logged in!")
    else:
        return render(request, "login.html", {})

def logout_view(request):
    logout(request)
    return render(request, "login.html", {})

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('signup')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})