 # -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render
from django.views.decorators.debug import sensitive_variables
from notifications.utils import send_template_mail, format_address
from users.utils import generate_password, sorted_categories
from users.models import UserProfile

@sensitive_variables('password')
@permission_required('auth.add_user')
def create(request):
    errors = []
    status = ''
    form_feedback = {}

    if 'submit' in request.POST:
        user = User()

        form_feedback['username'] = request.POST.get('username')
        form_feedback['email'] = request.POST.get('email')
        form_feedback['first_name'] = request.POST.get('first_name')
        form_feedback['last_name'] = request.POST.get('last_name')
        form_feedback['title'] = request.POST.get('title')
        form_feedback['display_name'] = request.POST.get('display_name')
        form_feedback['school'] = request.POST.get('school')
        form_feedback['bio'] = request.POST.get('bio')
        form_feedback['grade'] = request.POST.get('grade')
        form_feedback['phone'] = request.POST.get('phone')
        form_feedback['comment'] = request.POST.get('comment')

        username = request.POST.get('username')
        if username:
            if User.objects.filter(username=username).count() < 1:
                user.username = username
            else:
                errors += ['username', 'username_already_taken']
        else:
            errors += ['username', 'invalid_username']

        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        email = request.POST.get('email')
        try:
            validate_email(email)

            if User.objects.filter(email=email).count() < 1:
                user.email = email
            else:
                errors += ['email', 'email_already_taken']

        except ValidationError:
            errors += ['email', 'invalid_email']

        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')

        password = generate_password()
        user.set_password(password)

        if len(errors) < 1:
            user.save()

            user.profile.title = request.POST.get('title')
            user.profile.display_name = request.POST.get('display_name')
            user.profile.school = request.POST.get('school')
            user.profile.bio = request.POST.get('bio')
            user.profile.grade = request.POST.get('grade')
            user.profile.phone = request.POST.get('phone')
            user.profile.comment = request.POST.get('comment')
            user.profile.save()

            for group_id in request.POST.getlist('groups'):
                try:
                    user.groups.add(Group.objects.get(id=group_id))
                except Group.DoesNotExist: pass

            user.save()        # Save the groups information

            if request.POST.get('send_welcome_letter'):
                context = {
                    'sender': request.user,
                    'receiver': user,
                    'password': password,
                    'groups': [g.name for g in user.groups.all()],
                }

                sender_address = format_address(request.user.profile.name, request.user.email)
                receiver_address = format_address(user.profile.name, user.email)
                send_template_mail(sender_address, receiver_address, 'mail/user_welcome.html', context)

            status = 'success'
        else:
            status = 'error'

    return render(request, 'users/create.html', {
        'categories': sorted_categories(),
        'errors': errors,
        'status': status,
        'form_feedback': form_feedback,
    })
