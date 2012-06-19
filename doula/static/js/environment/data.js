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
        _mixin(this, __env);
        _mixin(this, AJAXUtil);
    },
    
    tagService: function(service, tag, tag_msg) {
        var msg = 'Tagging ' + service.name;
        var url = ['/envs', Data.name_url, service.name_url, 'tag'].join('/');
        var params = { 'tag' : tag, 'msg' : tag_msg };
        
        this.post(msg, url, params, this.doneTagService);
    },

    doneTagService: function(rlst) {
        service = Data.findServiceByID(rlst.service.name_url);
        service.tag = rlst.service.last_tag_service;
        service.msg = rlst.service.msg;
        service.status = rlst.service.status;

        UI.doneTagService(service.name_url);
    },

    tagEnv: function(tag, tag_msg) {
        var msg = 'Tagging Env';
        var url = '/tagsite';
        
        var params = {
            'site'        : Data.name_url,
            'tag'         : tag,
            'msg'         : tag_msg
        };
        
        this.post(msg, url, params, this.doneTagEnv, this.failedTagEnv);
    },

    doneTagEnv: function(rslt) {
        Data.status = rslt.site.status;
        Data.last_tag = rslt.site.last_tag;
        
        UI.doneTagService('site');
    },

    failedTagEnv: function() {
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