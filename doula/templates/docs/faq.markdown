Manager FAQs
===========

#### [How do I lock down a site?](#lock)
You'll be able to lockdown a site if you're part of the DoulaAdmins group. Visit the Doula home page and click on the site links. The 'Lock Site' button in the top right corner allows you to lock down a site. Remember that this means no one else will be able to release to this test site until it's been unlocked.

#### [How can I tell what's on production right now?](#prod)
This feature is coming to Doula. Stay tuned.

#### [How can tell see who's actually working right now?](#work)
Check the queue. Studies show there is a strong correlation between jobs created on Doula and work actually being done at Survey Monkey.

Engineering FAQs
===============

#### [Why is Doula unreacheable?](#unreachable)
Doula's heavily integrated with [GitHub Enterprise](http://code.corp.surveymonkey.com/) at Survey Monkey. Make sure that's up. If it is and Doula's still unreachable then how are you reading this? Contact devops@surveymonkey.com.

#### [How can I tell why my job failed?](#fail)
Visit the [Queue](http://doula.corp.surveymonkey.com/queue). Here you'll find a listing of all the jobs within the last 24 hours. Click on your job and you'll see a history and stack trace of why your job failed.

#### [Why doesn't my commit to the Config repository show?](#config)
Doula regularly polls the GitHub config repositories. If it's been longer than 10 minutes since you've updated the config repository visit this [link](http://doula.corp.surveymonkey.com/updatedoula). It asks Doula to request the latest information from GitHub. Your commit should show within ten minutes.

#### [How do I subscribe to job failures on Doula?](#subscribetofail)
Visit your own Doula [Settings Page](http://doula.corp.surveymonkey.com/settings). Click on the sites and services you'd like to subscribe to. You can also choose whether you receive emails on failure, success or never.