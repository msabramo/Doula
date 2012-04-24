// The SiteData Module
var SiteData = {
    
    name: '',
    name_url: '',
    nodes: { },
    applications: { },
    status: '',
    
    
    init: function() {
        _mixin(this, __site);
        _mixin(this, AjaxUtil);
    },
    
    tagApp: function(app, tag, msg) {
        var msg = 'Tagging application';
        var url = '/tag';
        var params = {
            'site'        : SiteData.name_url,
            'application' : app.name_url,
            'tag'         : tag,
            'msg'         : msg
        }
        
        this.post(msg, url, params, this.successfulDeployApplication);
    },
    
    successfulTagApp: function(rlst) {
        app = SiteData.findAppByID(rlst.app.name_url);
        app.tag = rlst.app.last_tag_app;
        app.msg = rlst.app.msg;
        app.status = rlst.app.status;
        
        Site.successfulTagApp(app);
    },

    deployApplication: function(app) {
        var msg = 'Deploying application';
        var url = '/deploy.json';
        var params = {
            'site'        : SiteData.name_url,
            'application' : app.name_url
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
        return this.applications[name_url];
    },
    
    isReadyForDeploy: function() {
        var isReadyForDeploy = true;
        
        for (var i=0; i < this.applications.length; i++) {
            if( this.applications[i].status != 'deployed' &&
                this.applications[i].status != 'tagged' ) {
                isReadyForDeploy = false;
                break;
            }
        }
        
        return isReadyForDeploy;
    }
};