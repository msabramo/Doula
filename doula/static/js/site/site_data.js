// The SiteData Module
var SiteData = {
    
    name: '',
    name_url: '',
    nodes: { },
    applications: { },
    status: '',
    token: '',
    
    init: function() {
        this.token = __token;
        _mixin(this, __site);
        _mixin(this, AjaxUtil);
    },
    
    tagApp: function(app, tag, msg) {
        var msg = 'Tagging ' + app.name;
        var tag_msg = $('#msg_' + app.name_url).val();
        var url = '/tag';
        var params = {
            'site'        : SiteData.name_url,
            'application' : app.name_url,
            'tag'         : tag,
            'msg'         : tag_msg
        }
        
        this.post(msg, url, params, this.doneTagApp);
    },
    
    doneTagApp: function(rlst) {
        app = SiteData.findAppByID(rlst.app.name_url);
        app.tag = rlst.app.last_tag_app;
        app.msg = rlst.app.msg;
        app.status = rlst.app.status;
        
        UI.doneTagApp(app);
    },

    deployApplication: function(app) {
        var msg = 'Marking application as deployed';
        var url = '/deploy';
        
        var params = {
            'site'        : SiteData.name_url,
            'application' : app.name_url,
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