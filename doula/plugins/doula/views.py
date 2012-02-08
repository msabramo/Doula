from doula.resources import App
from pyramid.view import view_config

def includeme(config):
    config.scan(__name__)
    config.add_route('show_doula', '/doula/', factory=App.root_factory)

@view_config(route_name="show_doula", renderer='doula_home.html', context=App)
def show_doula(context, request):
	# make call to backend here
	services = get_services()

	return { 'services' : services }

def get_services():
	return [
		{
			"id"      : 1,
			"name"    : "anonweb",
			"status"  : "unchanged",
			"tags"    : ["ehdalkd", "ehldkda"],
			"changes" : ["Changed 3 files", "Added 10 files"]
		},
		{
			"id"      : 2,
			"name"    : "create web",
			"status"  : "notreadyforrelease",
			"tags"    : ["dkllkd3", "ddggg9"],
			"changes" : ["Deleted 10 files", "Added 2 files"]
		},
		{
			"id"      : 2,
			"name"    : "analyze",
			"status"  : "configreadyforrelease",
			"tags"    : ["dkllkd3", "ddggg9"],
			"changes" : ["Deleted 10 files", "Added 2 files"]
		}
	]