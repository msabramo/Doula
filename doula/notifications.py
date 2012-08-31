from doula.models.user import User
from jinja2 import Environment, PackageLoader
from pyramid_mailer.mailer import Mailer
from pyramid_mailer.message import Message
from doula.log import get_log
from sets import Set

env = Environment(loader=PackageLoader('doula', 'templates'))


def email_success(email_list, job_dict):
    user = User.find(job_dict['user_id'])
    template = env.get_template('emails/job_success.html')

    body = template.render({
            'user': user,
            'job_dict': job_dict
        })

    if job_dict['job_type'] == 'push_to_cheeseprism':
        package = job_dict['service'] + ' ' + job_dict['version']
        subject = 'Doula Success: Pushed %s to Cheese Prism on %s' % package
    elif job_dict['job_type'] == 'cycle_services':
        subject = 'Doula Success: Cycled %s on %s' % (job_dict['service'], job_dict['site'])
    elif job_dict['job_type'] == 'push_service_environment':
        vals = (job_dict['service_name'], job_dict['site_name_or_node_ip'])
        subject = 'Doula Success: Released service %s on %s' % vals
    else:
        subject = 'Doula Success'

    email(subject, email_list, body)


def email_fail(email_list, job_dict, exception):
    user = User.find(job_dict['user_id'])
    template = env.get_template('emails/job_failure.html')

    body = template.render({
        'user': user,
        'job_dict': job_dict,
        'log': get_log(job_dict['id'])
    })

    if job_dict['job_type'] == 'push_to_cheeseprism':
        vals = (job_dict['service'], job_dict['remote'])
        subject = 'Doula Failure: Push %s to Cheese Prism on %s failed' % vals
    elif job_dict['job_type'] == 'cycle_services':
        subject = 'Doula Failure: Cycle %s on %s failed' % (job_dict['service'], job_dict['site'])
    elif job_dict['job_type'] == 'push_service_environment':
        vals = (job_dict['service_name'], job_dict['site_name_or_node_ip'])
        subject = 'Doula Failure: Release service %s on %s' % vals
    else:
        subject = 'Doula Failure'

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
                email_list.add(user['email'])
            elif job_dict['status'] == 'failed' and user['settings']['notify_me'] in ['always', 'failure']:
                email_list.add(user['email'])

    return [email for email in email_list]


def send_notification(job_dict, exception=None):
    """
    We only send out notifications for jobs initiated by users
    which are push to cheese prism, cycle services and release service
    """
    if job_dict['job_type'] in ['push_to_cheeseprism', 'cycle_services', 'push_service_environment']:
        email_list = build_email_list(job_dict)

        if len(email_list) > 0:
            if job_dict['status'] == 'complete':
                email_success(email_list, job_dict)
            elif job_dict['status'] == 'failed':
                email_fail(email_list, job_dict, exception)
