// The Data Module
var Data = {
    
    name: '',
    last_tag: '',
    name_url: '',
    nodes: { },
    services: { },
    status: '',
    token: '',
    
    init: function() {
        this.token = __token;
        _mixin(this, __site);
        _mixin(this, AJAXUtil);
    },
    
    tagService: function(service, tag, tag_msg) {
        var msg = 'Tagging ' + service.name;
        var url = ['/sites', Data.name_url, service.name_url, 'tag'].join('/');
        var params = { 'tag' : tag, 'msg' : tag_msg };
        
        this.post(msg, url, params, this.doneTagService);
    },

    doneTagService: function(rlst) {
        this.services[rlst.service.name_url] = rlst.service;
        UI.doneTagService(rlst.service);
    },

    tagSite: function(tag, tag_msg) {
        var msg = 'Tagging Site';
        var url = '/tagsite';
        
        var params = {
            'site'        : Data.name_url,
            'tag'         : tag,
            'msg'         : tag_msg
        };
        
        this.post(msg, url, params, this.donetagSite, this.failedtagSite);
    },

    donetagSite: function(rslt) {
        Data.status = rslt.site.status;
        Data.last_tag = rslt.site.last_tag;
        
        UI.doneTagService('site');
    },

    failedtagSite: function() {
        UI.failedTag();
    },
    
    revertServiceTag: function(service, tag, msg) {
      service.tag = tag;
      service.msg = msg;
      service.status = service.originalStatus;
    },
    
    findServiceByID: function(name_url) {
        return this.services[name_url];
    },
    
    isReadyForDeploy: function() {
        var isReadyForDeploy = true;
        
        for (var i=0; i < this.services.length; i++) {
            if( this.services[i].status != 'deployed' &&
                this.services[i].status != 'tagged' ) {
                isReadyForDeploy = false;
                break;
            }
        }
        
        return isReadyForDeploy;
    }
};