from coffin.shortcuts import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, mail_admins
from django.template import defaultfilters
import time, hashlib, random, datetime

def request_ip(request):
    return request.META.get('HTTP_X_FORWARDED_FOR', '') or request.META.get('REMOTE_ADDR')

# https://docs.djangoproject.com/en/dev/topics/email/#sending-alternative-content-types
def send_html_email(template_path, context, subject, from_email, to_emails):
    """Renders an email template using render_to_string twice, once with render_type = 'text'
    and once with render_type = 'html', then sends an email with the given parameters
    with a text/html alternative."""

    # render templates
    context['render_type'] = 'text'
    text_content = render_to_string(template_path, context)
    context['render_type'] = 'html'
    html_content = render_to_string(template_path, context)
    html_content = defaultfilters.linebreaks(html_content)

    # send email
    message = EmailMultiAlternatives(subject, text_content, from_email, to_emails)
    message.attach_alternative(html_content, 'text/html')
    message.send()

    return True

def generate_activation_key(row_id, value, salt=None, include_time=False):
    if isinstance(value, unicode):
        value = value.encode('utf-8')

    if salt is None and hasattr(settings, 'KEY_GENERATION_SALT'):
        salt = KEY_GENERATION_SALT

    if include_time:
        hash_me = '%s|%s|%s|%s' % (str(row_id), value, salt, str(time.time()))
    else:
        hash_me = '%s|%s|%s' % (str(row_id), value, salt)
    return hashlib.md5(hash_me).hexdigest()


def mail_admins_template(subject, template, context, fail_silently=False, connection=None, html_template=None):
    """Accepts a subject, template, context, (and optionally fail_silently,
    connection, and html_template), renders the template(s) using the context,
    and mails the admins using the templates and parameters via django.core.mail.mail_admins"""

    # render the message template - or fall back to blank if none given - requires html_template
    if not template and html_template:
        message = ''
    else:
        message = render_to_string(template, context)

    # renders html_template if applicable
    html_message = None
    if html_template:
        html_message = render_to_string(html_template, context)

    # sends the email
    mail_admins(subject, message, fail_silently, connection, html_message)

def get_timestamp(dt):
    """
    Accepts a datetime and returns the seconds since the epoch. Does not
    try to account for any issues with dates where this doesn't make sense
    (before or after the limits of the unix timestamp)
    """
    return (dt - datetime.datetime(1970, 1, 1)).total_seconds()
