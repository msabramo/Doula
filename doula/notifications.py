from doula.log import get_log
from doula.models.user import User
from doula.util import dumps
from doula.helper_filters import relative_datetime_from_epoch_time
from jinja2 import Environment, PackageLoader
from pyramid_mailer.mailer import Mailer
from pyramid_mailer.message import Message
from sets import Set
import traceback

env = Environment(loader=PackageLoader('doula', 'templates'))


def email_success(email_list, job_dict):
    user = User.find(job_dict['user_id'])
    template = env.get_template('emails/job_success.html')

    body = template.render({
            'user': user,
            'job_dict': job_dict,
            'date_and_time': relative_datetime_from_epoch_time(job_dict['time_started'])
        })

    subject = 'Doula Success: '

    if job_dict['job_type'] == 'build_new_package':
        vals = (user['username'],
                job_dict['package_name'],
                job_dict['version'])

        subject += '%s Built Package %s Version %s' % vals
    elif job_dict['job_type'] == 'cycle_service':
        vals = (user['username'], job_dict['service'], job_dict['site'])
        subject += '%s Cycled %s on %s' % vals
    elif job_dict['job_type'] == 'release_service':
        vals = (user['username'], job_dict['service'], job_dict['site'])
        subject += '%s Released Service %s on %s' % vals

    email(subject, email_list, body)


def email_fail(email_list, job_dict, exception):
    user = User.find(job_dict['user_id'])
    template = env.get_template('emails/job_failure.html')

    body = template.render({
        'user': user,
        'job_dict': job_dict,
        'log': get_log(job_dict['id']),
        'date_and_time': relative_datetime_from_epoch_time(job_dict['time_started'])
    })

    subject = 'Doula Failure: '

    if job_dict['job_type'] == 'build_new_package':
        vals = (user['username'], job_dict['package_name'])
        subject += '%s\'s Job to Build Package %s Failed' % vals
    elif job_dict['job_type'] == 'cycle_service':
        vals = (user['username'], job_dict['service'], job_dict['site'])
        subject += '%s\'s Job to Cycle %s on %s Failed' % vals
    elif job_dict['job_type'] == 'release_service':
        vals = (user['username'], job_dict['service'], job_dict['site'])
        subject += '%s\'s Job to Release Service %s on %s Failed' % vals

    email(subject, email_list, body)


def email(subject=None, recipients=None, body=None):
    mailer = Mailer(host='192.168.101.5')
    message = Message(subject=subject,
                      sender='doulabot@surveymonkey.com',
                      recipients=recipients,
                      html=body)

    mailer.send_immediately(message)


def build_email_list(job_dict):
    """
    Build a list of the emails that should be notified about a job.
    Users are notified about jobs if they've either created the job themselves
    or subscribed to the site or service for notifications.
    """
    email_list = Set([])

    for user in User.users():
        is_subscribed_to_this = False

        if user['username'] == job_dict['user_id']:
            is_subscribed_to_this = True
        elif job_dict['site'] in user['settings']['subscribed_to']:
            is_subscribed_to_this = True
        elif job_dict['service'] in user['settings']['subscribed_to']:
            is_subscribed_to_this = True

        if is_subscribed_to_this:
            if job_dict['status'] == 'complete' and user['settings']['notify_me'] == 'always':
                if user['email'] and user['email'] != 'null':
                    email_list.add(user['email'])
            elif job_dict['status'] == 'failed' and user['settings']['notify_me'] in ['always', 'failed']:
                if user['email'] and user['email'] != 'null':
                    email_list.add(user['email'])

    return [email for email in email_list]


def send_notification(job_dict, exception=None):
    """
    We only send out notifications for jobs initiated by users
    which are push to cheese prism, cycle services and release service
    """
    try:
        if job_dict:
            emailable_jobs = [
                'build_new_package',
                'cycle_service',
                'release_service']

            if job_dict['job_type'] in emailable_jobs:
                email_list = build_email_list(job_dict)

                if len(email_list) > 0:
                    if job_dict['status'] == 'complete':
                        email_success(email_list, job_dict)
                    elif job_dict['status'] == 'failed':
                        email_fail(email_list, job_dict, exception)
    except Exception as e:
        # error trying to notify user
        subject = 'Error notifying user: ' + e.message
        email_list = ['alexv@surveymonkey.com']
        body = dumps(job_dict) + "\n\n<br /><br />"
        body += traceback.format_exc()
        email(subject, email_list, body)
