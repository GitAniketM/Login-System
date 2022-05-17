from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from loginsystem import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import generate_token

# Create your views here.
def home(request):
    return render(request, "index.html")

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST['psswrd']
        cpassword = request.POST['psswrd2']

        if User.objects.filter(username = username):
            messages.error(request, "Username already exist.")
            return redirect('home')

        if User.objects.filter(email = email):
            messages.error(request, "Email already registered !!")
            return redirect('home')

        if len(username) > 10:
            messages.error(request, "Username must be within 10 characters.")

        if password != cpassword:
            messages.error(request, "Passwords didn't match !")

        if not username.isalnum():
            messages.error(request, "Username must contain only letters and numbers")
            return redirect('home')

        myuser = User.objects.create_user(username, email, password)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False

        myuser.save()  # saving the user in the database

        messages.success(request, "YOUR ACCOUNT IS SUCCESSFULLY CREATED. We have sent you a confirmation email. \n Please confirm your email in order to activate your account.")

        # Welcome Email
        subject = "Welcome to GFG -  Django Login !!"
        message = "Hello" + myuser.first_name + "!! \n" + "Welcome to GFG !! \n" + "Thank you for visiting the website \n We have also sent you a confirmation email, please confirm your email address in order to activate your account. \n\n Thanking You\nAniket"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)


        # Email Address confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your email @GFG - Django Login!!"
        message2 = render_to_string('email_confirmation.html', {
            'name' : myuser.first_name,
            'domain' : current_site.domain,
            'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token' : generate_token.make_token(myuser),
        })

        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silenty = True
        email.send()


        return redirect('signin')

    return render(request, "signup.html")

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psswrd--signin']

        user = authenticate(username = username, password=password)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, 'index.html', {'fname':fname})

        else:
            messages.error(request, "Username/Password Incorrect.")

    return render(request, "signin.html")

def signout(request):
    logout(request)
    messages.success(request, 'LOGGED OUT SUCCESSFULLY')
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not token and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'failed.html')

