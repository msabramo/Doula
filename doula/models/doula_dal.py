from doula.cache import Redis
from doula.util import dirify
from doula.models.model_factory import ModelFactory
from doula.util import dumps
import logging
import simplejson as json

log = logging.getLogger('doula')


class DoulaDAL(object):
    """
    The Doula Data Access Layer class handles access to the site and
    services stored in Doula's memory store (redis)
    """

    def __init__(self):
        self.redis = Redis.get_instance()
        self.mf = ModelFactory()

    #######################################
    # Build Site and Services From Bambinos
    #######################################

    def update_site_and_service_models(self):
        """
        Pull all the site data from the Bambinos. Ask the ModelFactory to
        build the model objects and finally save to redis
        """
        pipeline = self.redis.pipeline()
        all_registered_sites = self.get_all_registered_sites()

        all_sites = self.mf.pull_and_build_sites(all_registered_sites)

        for name, site in all_sites.iteritems():
            # Save the entire site and it's services
            pipeline.sadd('doula.sites', site.name)
            pipeline.set('doula.site:%s' % site.name, dumps(site))

            # Save the individual service
            for service_name, service in site.services.iteritems():
                vals = (site.name, service.name)
                # save the individual service as json
                pipeline.set('doula.service:%s:%s' % vals, dumps(service))
                # save the services as a set of the site
                pipeline.sadd('doula.site.services:%s' % site.name, service.name)

        pipeline.execute()

    def delete_site_from_cache(self, site_name):
        """
        Delete the site and all it's services from cache
        """
        # delete the site and remove it from the set
        self.redis.srem('doula.sites', site_name)
        self.redis.delete('doula.site:%s' % site_name)

        services_list = self.redis.smembers('doula.site.services:%s' % site_name)

        for service_name in services_list:
            # delete the services for the site
            vals = (site_name, service_name)
            self.redis.delete('doula.service:%s:%s' % vals)
            # delete the service from the set of service
            self.redis.srem('doula.site.services:%s' % site_name, service_name)

    #############################################
    # Pull the Site or Service Objects From Cache
    #############################################

    def get_all_sites(self):
        """
        Return all the site objects
        """
        sites = {}

        for site_name, registered_site in self.get_all_registered_sites().iteritems():
            sites[site_name] = self.find_site_by_name(site_name)

        return sites

    def find_site_by_name(self, site_name):
        """
        Find a site by name in redis. Site will contain nodes and services.
        """
        site_as_json = self.redis.get('doula.site:%s' % site_name)

        if site_as_json:
            return self.mf.build_site_from_cache(json.loads(site_as_json))
        else:
            raise Exception('Unable to find site %s' % site_name)

    def find_service_by_name(self, site_name, service_name):
        """
        Find a service for a site by name. Service will contain nodes.
        """
        vals = (site_name, service_name)
        service_as_json = self.redis.get('doula.service:%s:%s' % vals)

        if service_as_json:
            return self.mf.build_service_from_cache(json.loads(service_as_json))
        else:
            raise Exception("Unable to find service %s for site %s" % vals)

    #############################
    # Bambino Register/Unregister
    #############################

    def register_node(self, node):
        """
        Register a bambino with Doula. The node is a simple dict.

        Example Node:
            {
                "url": "http://5.5.0.66:6542",
                "ip": "5.5.0.66",
                "name": "mt1",
                "site": "mt1"
            }

        Example Site:
            {
                "name": "mtclone",
                "nodes": {
                    "mtclone-pyweb01": {
                        "url": "http://192.168.4.13:6666",
                        "ip": "192.168.4.13",
                        "name": "mtclone-pyweb01",
                        "site": "mtclone"
                    }
                }
            }
        """
        # The names should always be dirified, makes them comparable
        # that way we can ignore casing and other odd characters
        node["name"] = dirify(node["name"])
        node["site"] = dirify(node["site"])
        registered_site = self.get_registered_site(node['site'])

        log.debug('Registering Site')
        log.debug(json.dumps(registered_site))

        if node['name'] in registered_site['nodes']:
            registered_site['nodes'][node['name']] = node
            self.save_registered_site(registered_site)
        else:
            # If the node doesn't already exist for the site, add it
            # and update every one of the sites
            registered_site['nodes'][node['name']] = node
            self.save_registered_site(registered_site)
            self.update_site_and_service_models()

    def unregister_node(self, node):
        """
        Unregister a bambino node with Doula.

        Example Node:
            {
                "url": "http://5.5.0.66:6542",
                "ip": "5.5.0.66",
                "name": "mt1",
                "site": "mt1"
            }
        """
        registered_site = self.get_registered_site(node['site'])
        del registered_site['nodes'][node['name']]

        self.save_registered_site(registered_site)

    def save_registered_site(self, registered_site):
        """
        Save the registered site in it's current state.

        If the site no longer has nodes. Delete it altogether.

        If the site was just added, add it to the list of doula.sites
        """
        registered_site_redis_key = self.get_registered_site_redis_key(registered_site['name'])

        if len(registered_site['nodes']) > 0:
            self.redis.set(registered_site_redis_key, json.dumps(registered_site))
            self.redis.sadd("doula.registered.sites", registered_site["name"])
        else:
            # Registered Site has 0 nodes. delete the registered site as well
            self.redis.delete(registered_site_redis_key)
            self.redis.srem("doula.registered.sites", registered_site['name'])
            self.delete_site_from_cache(registered_site['name'])

    def get_registered_site(self, site_name):
        """
        Return a site that has registered with Doula as a dictionary.
        If the site doesn't exist return an empty site dictionary, without
        any node values. Those get added in the register_node call

        Example registered site:
            {
                "name": "mt1",
                "nodes": {
                    "mt1-pyweb01": {
                        "url": "http://192.168.4.41:6666",
                        "ip": "192.168.4.41",
                        "name": "mt1-pyweb01",
                        "site": "mt1"
                    },
                    "mt1-pyapp01": {
                        "url": "http://192.168.23.21:6666",
                        "ip": "192.168.23.21",
                        "name": "mt1-pyapp01",
                        "site": "mt1"
                    }
                }
            }
        """
        registered_site_as_json = self.redis.get(self.get_registered_site_redis_key(site_name))

        if registered_site_as_json:
            return json.loads(registered_site_as_json)
        else:
            msg = "Unable to find site. Creating new site dict for '%s'" % site_name
            log.info(msg)

            return {'name': site_name, 'nodes': {}}

    def get_registered_site_redis_key(self, name):
        return 'doula.registered.site:' + dirify(name)

    #######################
    # Utility Functions
    #######################

    def get_all_bambino_ips(self):
        ips = []
        all_sites = self.get_all_sites()

        for site_name, site in all_sites.iteritems():
            for node_name, node in site.nodes.iteritems():
                ips.append(node.ip)

        return ips

    def list_of_sites_and_services(self):
        """
        Return the sites and services as lists
        """
        sites = {}
        services = {}

        for site_name, registered_site in self.get_all_registered_sites().iteritems():
            sites[site_name] = site_name

            # save the services as a set of the site
            for service_name in self.redis.smembers('doula.site.services:%s' % site_name):
                services[service_name] = service_name

        return {'sites': sites.keys(), 'services': services.keys()}

    def get_all_registered_sites(self):
        """
        Get a list of the sites that are registered
        Returned objects are dictionaries

        Site is a dict:
            {
                'name':'mt1',
                'nodes': [{
                    'name': {
                        'name':value,
                        'site':value,
                        'url':value
                    }
                }]
            }

        Returns:
            {
                "name": {
                    'name':'mt1',
                    'nodes': [{
                        'name': {
                            'name':value,
                            'site':value,
                            'url':value
                        }
                    }]
                }
            }
        """
        registered_sites = {}

        for site_name in self._get_all_registered_site_names():
            registered_sites[site_name] = self.get_registered_site(site_name)

        return registered_sites

    def _get_all_registered_site_names(self):
        """Return the names registered."""
        site_names = self.redis.smembers("doula.registered.sites")
        return [site for site in site_names]
