#### [Site](#site)

Engineering at Survey Monkey runs different versions of SurveyMonkey.com for active development and testing. Doula refers to each instance of SurveyMonkey.com as a site. Internally each site is referred to as a monkey test environment.

#### [Monkey Test Environment](#mt)

Engineering at Survey Monkey refers to each instance of SurveyMonkey.com as a monkey test environment. Doula refers to each monkey test environment as a [Site](#site)

#### [Node](#service)

A node is server or [virtual machine](http://en.wikipedia.org/wiki/Virtual_machine) that runs one or more services.

#### [Service](#service)

SurveyMonkey.com is built as a [service oriented architechture](http://en.wikipedia.org/wiki/Service-oriented_architecture). This means the site's functionality is broken up into individual services. There are currently over 20 services that make up SurveyMonkey.com.

#### [Queue](#queue)

Since many of the tasks that Doula handles take longer than a few milliseconds Doula must schedule tasks. The [Queue](http://doula.corp.surveymonkey.com/queue) is the dashboard for all theses tasks. Each task has a title, status and log information.

#### [Github Enterprise](#github)

Survey Monkey engineering uses Git for version control. [Github Enterprise](http://code.corp.surveymonkey.com/) is the internally hosted instance of [Github](http://github.com) used by engineering.

#### [CheesePrism](#cheeseprism)

[CheesePrism](http://yorick.corp.surveymonkey.com:9003/) is the internally hosted instance of [PyPi](http://pypi.python.org/pypi) that hosts every python package developed or used as a dependency for SurveyMonkey.com.

#### [PIP](#pip)

This is a tool for installing and managing Python packages, such as those found in the Python Package Index.

#### [PyPi](#pypi)

The Python Package Index is a repository of software for the Python programming language

#### [Service Environment](#se)

A service environment is a virtual environment for a Survey Monkey service and all it's configuration files.

#### [Virtual Environment](#ve)

A virtual environment is a tool to create isolated Python environments.

#### [Supervisor](#sup)

Supervisor is a client/server system that allows its users to control a number of processes on UNIX-like operating systems.
