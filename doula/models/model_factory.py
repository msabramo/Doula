from doula.models.node import Node
from doula.models.service import Service
from doula.models.site import Site
from doula.util import dirify
import logging

log = logging.getLogger('doula')


class ModelFactory(object):
    """
    Model Factory handles creating sites, services and node objects
    """

    ################################
    # Pull newest data from Bambinos
    ################################

    def pull_and_build_sites(self, all_registered_sites):
        """
        Pulls the sites as dicts, creates a site object
        and ask the site object to update itself from all the nodes

        Example sites_as_dicts:
            [
            {
                "nodes": {
                    "mtclone-pyweb01": {
                        "url": "http://192.168.4.13:6666",
                        "ip": "192.168.4.13",
                        "name": "mtclone-pyweb01",
                        "site": "mtclone"
                    }
                },
                "name": "mtclone"
            }
            ]
        """
        sites = {}

        for site_name, registered_site in all_registered_sites.iteritems():
            # get the site nodes
            nodes = self._build_nodes_from_bambino_dicts(registered_site['nodes'])
            # build a site without the services
            site = Site(registered_site['name'], status='unknown', nodes=nodes)
            # get the services for the site
            site.services = self._get_updated_site_services(site)

            sites[site.name] = site

        return sites

    def _build_nodes_from_bambino_dicts(self, nodes_as_dicts):
        """
        Return node objects from the nodes as dicts dictionary using the
        Bambino data.

        The nodes will still be missing the config dict and supervisor_service_names
        list.

        Example nodes_as_dicts
            {
                "mtclone-pyweb01": {
                    "url": "http://192.168.4.13:6666",
                    "ip": "192.168.4.13",
                    "name": "mtclone-pyweb01",
                    "site": "mtclone"
                }
            }

        Example nodes:
            nodes = {
                "node_name": Node Object
            }
        """
        nodes = {}

        for node_name, node_as_dict in nodes_as_dicts.iteritems():
            nodes[node_name] = Node(node_name,
                                    dirify(node_as_dict['site']),
                                    node_as_dict['url'],
                                    node_as_dict['ip'])

        return nodes

    def _get_updated_site_services(self, site):
        """
        Poll the Bambino's registerd with this site and pull the
        latest information about their services.

        Aggregate the services across multiple nodes. Create new node
        objects just for the service. Each service gets it's own set
        of node objects.
        """
        services = {}

        for node_name, node in site.nodes.iteritems():
            services_as_dicts = node.pull_services_as_dicts()

            for service_as_dict in services_as_dicts['services']:
                service = self._update_or_create_service(services, service_as_dict, node)
                services[service.name] = service

        return services

    def _update_or_create_service(self, services, service_as_dict, node):
        """
        Return the updated or new service. If the service already exist
        we only want to update the node specific data.
        """
        service = None

        if service_as_dict['name'] in services:
            service = services[service_as_dict['name']]
        else:
            service_as_dict['site_name'] = node.site_name
            service = Service(**service_as_dict)

        # Everything that is unique to a node is held here. It's basically
        # the config files, changed_files and supervisor_service_names
        service.append_node(node, service_as_dict)

        return service

    ################################
    # Build Model Objects From Redis
    ################################

    def build_site_from_cache(self, site_as_dict):
        """
        Build a site from the cached redis data
        """
        site = Site(site_as_dict['name'], site_as_dict['status'])
        site.nodes = self._build_nodes_from_from_cached_dicts(site_as_dict['nodes'])
        site.services = self._build_site_services_from_dict(site_as_dict['services'])

        return site

    def _build_nodes_from_from_cached_dicts(self, nodes_as_dicts):
        """
        Return node objects from the nodes as dicts dictionary using the
        cached data.

        The nodes will still be missing the config dict and supervisor_service_names
        list.

        Example nodes_as_dicts
            {
                "mtclone-pyweb01": {
                    "url": "http://192.168.4.13:6666",
                    "name": "mtclone-pyweb01",
                    "site_name": "mtclone"
                }
            }

        Example nodes:
            nodes = {
                "node_name": Node Object
            }
        """
        nodes = {}

        for node_name, node_as_dict in nodes_as_dicts.iteritems():
            nodes[node_name] = Node(node_name,
                                    node_as_dict['site_name'],
                                    node_as_dict['url'],
                                    node_as_dict['ip'])

        return nodes

    def _build_site_services_from_dict(self, services_as_dicts):
        services = {}

        for service_name, service_as_dict in services_as_dicts.iteritems():
            services[service_name] = self.build_service_from_cache(service_as_dict)

        return services

    def build_service_from_cache(self, service_as_dict):
        """
        Build a single service from the cached redis data
        """
        service = Service(**service_as_dict)

        # Add the nodes to the services
        for node_name, node_as_dict in service_as_dict['nodes'].iteritems():
            node = Node(node_as_dict['name'],
                        node_as_dict['site_name'],
                        node_as_dict['url'],
                        node_as_dict['ip'])
            service.append_node(node, service_as_dict)

        return service
