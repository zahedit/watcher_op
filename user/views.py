from django.contrib.auth import login, get_user_model
from django.views.generic import FormView, UpdateView, DetailView
from .forms import RegistrationForm, LoginForm, UserUpdateForm
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.contrib.auth import login
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required

User = get_user_model()

class RegisterView(FormView):
    """A view class that handles user registration."""

    form_class = RegistrationForm
    template_name = 'user/register.html'

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        current_site = get_current_site(self.request)
        mail_subject = _('Activate your blog account.')
        message = render_to_string('user/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
        email.send()
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super(RegisterView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, 'form submission success')
        return reverse('home')
#############################################
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.add_message(request, messages.INFO, 'Thank you for confirming your registration. You can now log in.again.')
        return redirect('home')

    else:
        messages.success(request, _("Invalid or expired token. Please try again."))
        return redirect('home')
#############################################
class LoginView(FormView):
    form_class = LoginForm
    template_name = 'user/login.html'
    success_url = '/'

    def form_valid(self, form):
        login(self.request, form.cleaned_data['user'])
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super(LoginView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, 'logged in')
        return reverse('home')
#############################################
# class ProfileUpdateView(LoginRequiredMixin, UpdateView):
#     model = User
#     fields = ('username', 'avatar', 'bio', 'website')
#     template_name = 'user/profile_update.html'
#     success_url = '/'

#     def get_object(self, queryset=None) :
#         return self.request.user
#############################################
@login_required
def logout_view(request):
	django_logout(request)
	messages.success(request, _("logged out successfully"))
	return redirect('home')
#############################################
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user/change_password.html', {
        'form': form
    })
#############################################
class ProfileView(DetailView):
    model = User
    template_name = "user/profile.html"
    context_object_name = "user"

    def get_object(self):
        username = self.kwargs.get("username")
        return User.objects.get(username=username)
#############################################
class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "user/profile_update.html"

    def get_form_kwargs(self):
        # Get the default form kwargs
        kwargs = super().get_form_kwargs()
        # Add the current user as the user parameter
        kwargs["user"] = self.request.user
        return kwargs

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, 'changes saved')
        return reverse('account')

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is logged in
        if request.user.is_authenticated:
            # If yes, proceed with the view
            return super().dispatch(request, *args, **kwargs)
        else:
            # If no, redirect to the login page
            return redirect('auth-login')
#############################################