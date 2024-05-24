from django.shortcuts import render, redirect
from django.urls import reverse
from google_auth_oauthlib.flow import Flow
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib.auth.models import User as  DjangoUser
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from user.models import Choices, User
from django.conf import settings
import re
import boto3

SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read', 
    'https://www.googleapis.com/auth/fitness.body.read', 
    'https://www.googleapis.com/auth/fitness.heart_rate.read', 
    'https://www.googleapis.com/auth/fitness.sleep.read',
    'https://www.googleapis.com/auth/fitness.blood_glucose.read',
    'https://www.googleapis.com/auth/fitness.blood_pressure.read',
    'https://www.googleapis.com/auth/fitness.body_temperature.read',
    'https://www.googleapis.com/auth/fitness.location.read',
    'https://www.googleapis.com/auth/fitness.nutrition.read',
    'https://www.googleapis.com/auth/fitness.oxygen_saturation.read',
    'https://www.googleapis.com/auth/fitness.reproductive_health.read'
]

PASSWORD_RESET_SUBJECT = "FitOn Account Password Reset Request"



def home_dashboard(request):
    return render(request, 'user/dashboard.html')

def logoutView(request):
    logout(request)
    return redirect("user:home_dashboard")

def loginView(request):
    if request.method == "POST":
        username = request.POST.get("user_email")
        password = request.POST.get("user_pwd")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print("Login successful")
            return redirect("user:account")  # Redirect to the home page after login

        else:
            messages.error(request, "Incorrect Credentials! User does not exist!")
            return redirect("user:login")
    template_name = "user/login.html"
    return render(request, template_name)

def user_exists(email):
    return User.objects.filter(email=email).exists()

def create_django_user(email, password, name):
    usr = DjangoUser.objects.create_user(email, email, password)
    usr.first_name = name
    usr.save()
    return usr

def create_user_profile(**kwargs):
    filtered_kwargs = {k: v for k, v in kwargs.items()}
    User.objects.create(**filtered_kwargs)

def register(request):
    if request.method == "POST":
        # Collecting data from the form
        form_data = get_form_data(request)
        if type(form_data) is str:
            messages.error(request, form_data)
            return HttpResponseRedirect(reverse("user:user_registration"))
        if user_exists(form_data["email"]):
            messages.error(request, "User already exists! Please go to login page.")
            return HttpResponseRedirect(reverse("user:user_registration"))
        # try:
        usr = create_django_user(
            form_data["email"], form_data["password"], form_data["name"]
        )
        pwd = form_data["password"]
        del form_data["password"]
        create_user_profile(**form_data)
        login(request, usr)
        print("User saved successfully")
        client = boto3.client('cognito-idp', region_name='us-east-1')
        
        response = client.sign_up(
            ClientId='48c6righn4ev7j9pqksehr4f1o',
            Username=form_data["email"],
            Password=pwd,
            UserAttributes=[
                {
                    'Name': 'custom:city',
                    'Value': form_data["city"]
                },
                {
                    'Name': 'custom:height',
                    'Value': form_data["height"]
                },
                {
                    'Name': 'custom:phone',
                    'Value': form_data["phone"]
                },
                {
                    'Name': 'custom:weight',
                    'Value': form_data["weight"]
                },
                # Add more attributes as needed
            ]
        )
        
        print(response)
            
        # except Exception as e:
        #     messages.error(
        #         request,
        #         "Failed to add new user! Invalid details / User already exists.",
        #     )
        #     print(e)
        #     return render(request, template_name="user/user_registration.html")

        return HttpResponseRedirect(
            reverse("user:account")
        )  # redirect to home page after successful registration
    
    else:
        return render(
            request, template_name="user/user_registration.html"
        )

def get_form_data(request):  # noqa: C901
    # Collecting data from the form
    name = request.POST.get("user_name") or None
    email = request.POST.get("user_email") or None
    phone = request.POST.get("user_phone") or None
    sex = request.POST.get("user_sex") or None
    password = request.POST.get("password") or None
    city = request.POST.get("city") or None
    height = request.POST.get("height") or None
    height_inches = request.POST.get("inches") or None
    height_unit = request.POST.get("height_unit") or None
    weight_unit = request.POST.get("weight_unit") or None
    weight = request.POST.get("weight") or None
    
    if (not height_unit) or (not weight_unit):
        return "Error: Invalid Units"
    
    if weight_unit == "lb" and weight is not None:
        weight = float(weight) * 0.453592 #Convert to kg
    
    if height_unit == "ft_in" and height is not None:
        #Convert to cm
        height = float(height) * 30.48
        if height_inches:
            height += float(height_inches) * 2.54

    form_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "sex": sex,
        "password": password,
        "city": city,
        "weight": weight,
        "height": height
    }

    if not isValidPassword(password):
        return "Error: Invalid Password"

    ret, msg = check_user_validity(form_data)

    if not ret:
        return msg

    return form_data

def isValidEmail(email):
    if not email:
        return False
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    return True

def check_user_validity(form_data):  # noqa: C901
    try:
        if not form_data["name"]:
            return False, "Error: Invalid Name"
        if not isValidEmail(form_data["email"]):
            return False, "Error: Invalid Email"
        if not form_data["phone"]:
            return False, "Error: Invalid Phone"
        if form_data["sex"] not in [opt[0] for opt in Choices.sex]:
            return False, "Error: Invalid Sex"
        if not form_data["city"]:
            return False, "Invalid City"
        if not form_data["city"]:
            return False, "Invalid City"
        if not form_data["height"]:
            return False, "Invalid Height"
        if not form_data["weight"]:
            return False, "Invalid Weight"

        return True, ""

    except Exception as e:
        print(e)
        return False, "Invalid User Details"

def passwordResetView(request):
    template_name = "user/resetPassword/password_reset.html"

    if request.method == "GET":
        return render(request, template_name)

    else:
        user_email = request.POST.get("user_email")
        if send_email(
            request,
            user_email,
            "user/resetPassword/template_reset_password.html",
            PASSWORD_RESET_SUBJECT,
        ):
            alert_message = "Email sent. Please follow the link to reset your password."
            messages.success(request, alert_message)
            return HttpResponseRedirect(reverse("user:login"))
        else:
            alert_message = (
                "Email not exists in our database. Please register a new account."
            )
            messages.error(request, alert_message)
            return HttpResponseRedirect(reverse("user:user_registration"))

def isValidPassword(password):
    if not password:
        return False
    if not len(password) >= 8:
        return False
    return True

def send_email(request, user_email, email_template, subject, **kwargs):
    try:
        user = User.objects.get(email=user_email)
        token_generator = PasswordResetTokenGenerator()
        context = kwargs
        context["user"] = user
        context["domain"] = get_current_site(request).domain
        context["uid"] = urlsafe_base64_encode(user.email.encode("utf-8"))
        context["token"] = token_generator.make_token(user)
        context["protocol"] = "https" if request.is_secure() else "http"
        message = render_to_string(
            email_template,
            context,
        )
        email = EmailMessage(subject, message, to=[user.email])
        if email.send():
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def passwordResetConfirmView(request, uidb64, token):
    template_name = "user/resetPassword/password_reset_confirm.html"
    if request.method == "GET":
        return render(request, template_name, {"uidb64": uidb64, "token": token})

    else:
        try:
            user_email = urlsafe_base64_decode(uidb64).decode("utf-8")
            new_password = request.POST.get("password")
            if not isValidPassword(new_password):
                raise Exception("Invalid Password")
            token_generator = PasswordResetTokenGenerator()
        except Exception as e:
            print(e)
            messages.error(request, "Invalid Details")
            return HttpResponseRedirect(reverse("user:passwordReset"))

        """
            verifying uid64
        """
        if User.objects.filter(username=user_email).exists():
            user = User.objects.get(username=user_email)
            """
                verifying token
            """
            if token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                alert_message = "Password reset successfully, please login."
                messages.success(request, alert_message)
                return HttpResponseRedirect(reverse("user:login"))
            else:
                alert_message = "Token invalid!"
                messages.error(request, alert_message)
                return HttpResponseRedirect(reverse("user:passwordReset"))

        else:
            alert_message = (
                "Some error exists when resetting your password, please try again."
            )
            messages.error(request, alert_message)
            return HttpResponseRedirect(reverse("user:passwordReset"))

def authorize_google_fit(request):
    credentials = request.session.get('google_fit_credentials')

    if not credentials or credentials.expired:
        if settings.DEBUG == True:
            flow = Flow.from_client_secrets_file('credentials.json', SCOPES)
        else:
            flow = Flow.from_client_config(settings.GOOGLEFIT_CLIENT_CONFIG, SCOPES)
        flow.redirect_uri = request.build_absolute_uri(reverse('user:callback_google_fit'))
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        request.session['google_fit_state'] = state

    return redirect(authorization_url)

def callback_google_fit(request):
    state = request.session['google_fit_state']
    
    if state:
        if settings.DEBUG == True:
            flow = Flow.from_client_secrets_file('credentials.json', SCOPES, state=state)
        else:
            flow = Flow.from_client_config(settings.GOOGLEFIT_CLIENT_CONFIG, SCOPES, state=state)
        flow.redirect_uri = request.build_absolute_uri(reverse('user:callback_google_fit'))
        flow.fetch_token(authorization_response = request.build_absolute_uri())
        
        credentials = flow.credentials
        request.session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
    return redirect(reverse("metrics:get_metric_data"))

def account_page(request):
    user = User.objects.get(email=request.user.username)
    return render(request, 'user/account.html', {'login_user': user})