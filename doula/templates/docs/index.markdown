Doula?
-----
[Doula](http://doula.corp.surveymonkey.com/) is a release management system developed at Survey Monkey to help engineering version and deploy the components that make up SurveyMonkey.com to multiple testing environments for development and quality assurance testing.

Because each testing environment is composed of over 20 python services that run on one or more servers, it is complex to manually update, version and cycle those services. Doula simplifies interactions with the testing environments. It handles all these tasks and provides status information and notifications to the software and quality assurance engineers actively developing SurveyMonkey.com.

Doula refers to each testing environment as a [site](/docs/glossary#site). Each site is composed of python services that are responsible for different parts of the site's functionality. Each service is composed of python packages and configuration files (INI files).

Below is a simplified overview of the process of getting a service released to a site. All of the python packages under development are hosted in an internal instance of [GitHub](http://code.corp.surveymonkey.com/organizations/devmonkeys). Code is first committed to a Git repository by a development team. Then it's bundled as a python package and hosted in an internal PyPi named CheesePrism. This package is then released to a monkey test environment as part of a service. Once released the service's config files are updated and the service is restarted.

<!-- todo: update the flow diagram. use new terms. expand a bit? -->

<img class="center" src="/images/docs/doula_overview.png" title="Doula Overview" />

Login
-----

<img class="right" src="/images/docs/doula_login.png" title="Doula Login" />

Doula authenticates against Survey Monkey's internal [GitHub](http://code.corp.surveymonkey.com/). The first time you login you'll be asked to authorize Doula to access your GitHub account. Once logged in you’ll have access to every part of the site.

All email notifications are sent to the email address associated with your GitHub account. To update the email address: logout of Doula, update your email address on GitHub and log back into Doula.

<!-- clear the section -->
<div class="group"></div>

Sites
-----

<img class="right" style="width: 40%;" src="/images/docs/doula_sites.png" title="Doula Sites" />

Every monkey test environment (currently [MT1](http://mt1-pyweb01/), [MT2](http://mktest2-py.corp.surveymonkey.com/) and [MT3](http://mktest3-py.corp.surveymonkey.com/) and MT4) is a site managed by Doula. Each site is composed of the individual services that make up the Survey Monkey website.

<!-- clear the section -->
<div class="group"></div>

Services
--------

<img class="right" src="/images/docs/doula_services.png" title="Doula Services" />

Since Survey Monkey is a service oriented architecture (SOA) the entire website is composed of over 20 individual python services. Each of these services is hosted in the [devmonkeys](http://code.corp.surveymonkey.com/organizations/devmonkeys) GitHub organization.

The devmonkeys organization has over 50 repositories being actively developed by Survey Monkey engineering.

<div class="group"></div>

#### Service Details and Admin Actions

There are two major actions for each service. The first action, Admin Actions, allows you to view the packages' Git commit history, build new packages and release a service to a testing environment. The second action, Edit Label, allows anyone to add a label to an existing service letting everyone know the current state of the service.

<img class="center" src="/images/docs/doula_service_actions.png" title="Service Action" />


<!-- clear the section -->
<div class="group"></div>

##### Package Commit History

Each Survey Monkey package's Git commit history is available in Admin Actions. Clicking on the packages's name shows the familiar GitHub commit history with quick links to Git diffs.

The active commit (the commit currently in the testing environment) is highlighted and marked as 'active package'. If no active package is found this means it wasn't found in the last 50 commits to the package's repository.

<img class="center" src="/images/docs/doula_git_commit_history.png" title="Doula Service Action" />

#### Build New Package

You can build a new python package from a Git repository. When you click the 'Build New Package' button you'll be prompted to select the branch and version number you'd like to release from. Doula now appends the branch **name** to the **version** number when you build a new package. This allows everyone to quickly see what branch a build came from.

After the package is built and pushed to CheesePrism it'll be available for release to a site.

<img class="center" src="/images/docs/doula_build_new_package.png" title="Doula Service Action" />


#### Cycle Service

Cycle Service shuts down a service and starts it back up again via Supervisor.

#### Release Service

Releasing a service means updating python packages and config files. Doula pip installs from CheesePrism and pulls config files from the GitHub config repository as part of creating a new release. The versions of the python packages and the config commit are chosen via the Doula UI.

The python packages available are pulled from CheesePrism. Doula polls CheesePrism regularly for the latest python packages.

Doula also polls the GitHub [config organization](http://code.corp.surveymonkey.com/config). Each service has a Git repository with a branch for each site. This means that if you want to update the config files for Anweb on MT1 you'll need to commit to the mt1 branch of the anweb repository you find [here](http://code.corp.surveymonkey.com/config/anweb).

<img class="center" src="/images/docs/doula_release.png" title="Doula Release" />

#### Lock Site

Sites on Doula can be locked by members of the DoulaAdmin group (made up of the technical leads at SurveyMonkey) on GitHub. When a site is locked everyone is prevented from releasing updates to python packages and config files. Only another technical lead can unlock a site.

<img class="center" src="/images/docs/doula_release_locked.png" title="Doula Release Locked" />


Queue
-----

Since many of the tasks that Doula handles take longer than a few seconds Doula must schedule tasks in a queue. The [Queue](http://doula.corp.surveymonkey.com/queue) is the dashboard for all theses tasks.

The Queue displays every job Doula is processing, has processed or failed to process. Every job contains detailed information about what went right or wrong when Doula processed the job. The job also includes details about when it was run and a stack trace if it failed.

You can filter jobs by status (Queued, Complete or Failed) and job creator (all jobs or jobs you created).

<img class="center" src="/images/docs/doula_queue.png" title="Doula Queue" />

<!-- clear the section -->
<div class="group"></div>

Settings
--------

Doula keeps notification settings for every user that logs in. By default Doula will send an email notification if a job you create fails. You can also subscribe to notifications to a site or service.

To get to the notifications page click the drop down in the top right corner and select the 'Settings' link.

<img class="center" src="/images/docs/doula_settings.png" title="Doula Settings" />
