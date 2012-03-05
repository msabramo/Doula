========
 Design
========


Traversal
=========


root:/
------

maps to the `bambino.resources.App` which is initialize on application initialization


site containter: /sites
-----------------------

Added by plugin at initialization.  getter searchs doula mapping of
registered sites.

::


 >>> def handle_bambino_reg(payload, sitemap):
 ...     nodemap = sitemap[payload['sitename']]
 ...     nodemap[payload['nodename']] = payload['address'] 
 ...     return True

 >>> sitemap = dict(
 ...   site1=dict(node1='someaddress'),
 ...   site2=dict(node2='someaddress2',
 ...              node3='someaddress3'),
 ...   )

 >>> sc = SiteContainer(sitemap)
 >>> sc.get('site3')
 KeyError('Not found')

 >>> sc.get('site1')
 < SiteEnvironment at ... site1: nodes: node1: someaddress >

All application environments may be identified by the triple 'site1:node1:appenv1'.

 >>> site2 = sc.get('site2')
 >>> site2.get('nodes')
 <NodeContainer at ... : node2:address, node3:address>

 >>> nodes = _
 >>> nodes.get('node2')
 < Node someaddress2 >

 >>> wtfc = node.what_changed()
 >>> site2.what_changed() == node.what_changed() + site2['nodes']['node3'].what_changed() 

[node.wtfc() for node in  context.nodes]


