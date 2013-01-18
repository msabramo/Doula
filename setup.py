import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

requires = [
    'APScheduler',
    'fabric',
    'gitpython',
    'Jinja2',
    'path.py',
    'pyramid',
    'pyramid-jinja2',
    'pyramid_debugtoolbar',
    'redis',
    'hiredis',
    'requests',
    'simplejson',
    'supervisor',
    'waitress',
    'retools',
    'pygments',
    'pyyaml',
    'pyramid_mailer',
    'markdown'
    ]

setup(name='Doula',
      version='0.1',
      description='Doula',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      data_files=[
        ('doula', ['*.markdown', '**/*.markdown'])
      ],
      setup_requires=[
        'egggitinfo'
      ],
      tests_require=requires,
      test_suite="doula",
      entry_points="""\
      [paste.app_factory]
      main = doula:main
      """
      )
