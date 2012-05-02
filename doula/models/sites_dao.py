import json
import logging

from doula.util import pprint
from doula.util import dirify
from doula.cache import Cache
from doula.models.sites import Site
from doula.models.sites import Node
from doula.models.sites import Application
from doula.models.sites import Package

log = logging.getLogger('doula')

class SiteDAO(object):
    def __init__(self):
        self.cache = Cache.cache()
        self.site_prefix = 'site:'
    
    def register_node(self, node):
        node = self._lower_keys(node)
        site = self._get_site(node['site'])
        site['nodes'][node['name']] = node
        
        key = self._get_site_cache_key(node['site'])
        
        log.info('Registering site')
        log.info(json.dumps(site))
        
        self.cache.set(key, json.dumps(site))
    
    def _lower_keys(self, node):
        lower_node = { }
        for k, v in node.iteritems():
            lower_node[k.lower()] = v.lower()
        return lower_node
    
    def unregister_node(self, node):
        site = self._get_site(node['site'])
        del site['nodes'][node['name']]

        key = self._get_site_cache_key(node['site'])
        self.cache.set(key, json.dumps(site))

        # If the site has no nodes left remove from cache
        if len(site['nodes']) == 0:
            self.cache.delete(key)

    def _get_site_cache_key(self, name):
        return self.site_prefix + dirify(name)
    
    def _get_site(self, name):
        """
        Get the site jsonified object from cache. If the site
        doesn't exist create one.
        Site is a dict:
            {'name':'value', 
            nodes: [{'name':{'name':value, 'site':value, 'url':value}}]}
        """
        site = self.cache.get(self._get_site_cache_key(name))
        
        if site:
            return json.loads(site)
        else:
            log.info('Unable to find site by name "{0}"'.format(name))
            return { 'name' : name, 'nodes' : { } }
    
    def nodes(self, name):
        site = self._get_site(name)
        
        return site['nodes']
    
    def _all_site_keys(self):
        site_keys = self.cache.keys('site:*')
        
        log.info('Site Keys')
        log.info(site_keys)
        
        if type(site_keys) == str:
            return [site_keys]
        else:
            return site_keys
    
    def get_sites(self):
        """
        Get list of registered sites. Returns actual Site object.
        """
        all_sites = { }
        
        for site_key in self._all_site_keys():
            site_name = site_key.replace(self.site_prefix, '')
            all_sites[site_name] = self.get_site(site_name)
        
        return all_sites
    
    def get_site(self, site_name):
        simple_site = self._get_site(site_name)
        return SiteFactory.build_site(simple_site)
    
    def get_master_site(self):
        """
        Return the master site. In prod will be MT1 or MTPrime.
        For Development the master site is mt1 if found or the first site found.
        """
        site_keys = self._all_site_keys()
        
        if len(site_keys) < 1:
            raise Exception("No sites registered")
        
        if "mt1" in site_keys:
            return "mt1"
        else:
            return site_keys[0].replace(self.site_prefix, '')
        
    
    @staticmethod
    def get_node_ips():
        dao = SiteDAO()
        ips = [ ]
        
        for site in dao.get_sites():
            key = dao._get_site_cache_key(site)
            site_obj = json.loads(dao.cache.get(key))
            
            for name, node in site_obj['nodes'].iteritems():
                ips.append(node['ip'])
        
        return ips
    
    @staticmethod
    def get_application(site, app):
        dao = SiteDAO()
        site = dao.get_site(site)
        return site.applications[app]

# alextodo, move this to a staticmethod on the Site object
class SiteFactory(object):
    """
    Builds Site objects, with Node and Applications as well
    """
    @staticmethod
    def build_site(simple_site):
        """
        Take the simple dictionary version of a site object, i.e.
            {name:value, nodes[{'name':value, 'site':value, 'url':value}]}
        and return an actual Site object with all the nodes and applications
        built as well.
        """
        site = Site(simple_site['name'])
        site.nodes = SiteFactory._build_nodes(simple_site['nodes'])
        site.applications = SiteFactory._get_combined_applications(site.nodes)
        
        return site
    
    @staticmethod
    def _build_nodes(simple_nodes):
        """
        Takes the nodes with format:
            nodes[{'name':value, 'site':value, 'url':value}]
        And builds Node objects
        """
        nodes = { }
        
        for name,n in simple_nodes.iteritems():
            node = Node(name, n['site'], n['url'])
            node.load_applications()
            nodes[name] = node
        
        return nodes
    
    @staticmethod
    def _get_combined_applications(nodes):
        """
        Takes the nodes (contains actual Node objects) and 
        builds the applications as a combined list of their 
        applications for the entire site.
        """
        combined_applications = { }
        
        for k, node in nodes.iteritems():
            for app_name, app in node.applications.iteritems():
                combined_applications[app_name] = app
        
        return combined_applications
