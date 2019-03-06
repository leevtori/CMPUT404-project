from django.contrib.auth import authenticate, login
# from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, HttpResponse

from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import get_object_or_404
from .models import User
from .forms import CustomUserCreationForm




def signup(request):
    if request.method == "POST":
        # form = UserCreationForm(request.POST)
        form = CustomUserCreationForm
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('signup')
    else:
        form = CustomUserCreationForm
    return render(request, 'signup.html', {'form': form})



# class SignUp(generic.CreateView):
#     form_class = CustomUserCreationForm
#     success_url = reverse_lazy('login')
#     template_name = 'signup.html'

    # def form_valid(self, form):
    #     obj = get_object_or_404(User, pk=self.kwargs['pk'])
    #     form.instance.pk = obj
    #     return super(SignUp, self).form_valid(form)