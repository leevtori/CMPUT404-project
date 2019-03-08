from django.urls import reverse_lazy
from django.views import generic
from .models import User
from .forms import CustomUserCreationForm
from django.contrib.messages.views import SuccessMessageMixin

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
    success_message = "Congratulations, you've successfully signed up! Wait to be approved."

    # def form_valid(self, form):
    #     obj = get_object_or_404(User, pk=self.kwargs['pk'])
    #     form.instance.pk = obj
    #     return super(SignUp, self).form_valid(form)