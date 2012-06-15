// The SiteData Module
var SiteData = {
    
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
        _mixin(this, AjaxUtil);
    },
    
    tagApp: function(app, tag, tag_msg) {
        var msg = 'Tagging ' + app.name;
        var url = '/tag';
        var params = {
            'site'        : SiteData.name_url,
            'service' : app.name_url,
            'tag'         : tag,
            'msg'         : tag_msg
        };
        
        this.post(msg, url, params, this.doneTagApp);
    },

    doneTagApp: function(rlst) {
        app = SiteData.findAppByID(rlst.app.name_url);
        app.tag = rlst.app.last_tag_app;
        app.msg = rlst.app.msg;
        app.status = rlst.app.status;
        
        UI.doneTagApp(app.name_url);
    },

    tagSite: function(tag, tag_msg) {
        var msg = 'Tagging Site';
        var url = '/tagsite';
        
        var params = {
            'site'        : SiteData.name_url,
            'tag'         : tag,
            'msg'         : tag_msg
        };
        
        this.post(msg, url, params, this.doneTagSite, this.failedTagSite);
    },

    doneTagSite: function(rslt) {
        console.log('done tagging site');
        console.log(rslt);

        SiteData.status = rslt.site.status;
        SiteData.last_tag = rslt.site.last_tag;
        
        UI.doneTagApp('site');
    },

    failedTagSite: function() {
        UI.failedTag();
    },

    deployApplication: function(app) {
        var msg = 'Marking service as deployed';
        var url = '/deploy';
        
        var params = {
            'site'        : SiteData.name_url,
            'service' : app.name_url,
            'token'       : SiteData.token,
            'tag'         : app.last_tag_app.name
        }
        
        this.post(msg, url, params, this.successfulDeployApplication);
    },
    
    successfulDeployApplication: function(rslt) {
        app = SiteData.findAppByID(rslt.app.name_url);
        app.status = rslt.app.status;
        UI.deployApp(app);
    },
    
    revertAppTag: function(app, tag, msg) {
      app.tag = tag;
      app.msg = msg;
      app.status = app.originalStatus;
    },
    
    findAppByID: function(name_url) {
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