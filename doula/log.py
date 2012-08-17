from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import BashLexer
import os


def get_log(job_id):
    """
    Grabs a log file for a job and highlights the text with Pygments
    for display to the user
    """
    log = ''
    log_name = os.path.join('/var/log/doula', job_id + '.log')

    with open(log_name) as log_file:
        log = log_file.read()

    return highlight(log, BashLexer(), HtmlFormatter())
