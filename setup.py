from setuptools import find_packages
from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'waitress',
    'path.py',
    'pyramid-socketio'
    ]

setup(name='Doula',
      version='0.0',
      description='Doula',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='SurveyMonkey DevOps et. al',
      author_email='whit-at-surveymonkey-dot-com',
      url='http://github.com/SurveyMonkey/Doula',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="Doula",
      entry_points = """\
      [paste.app_factory]
      main = doula.wsgiapp:main
      """,
      )

