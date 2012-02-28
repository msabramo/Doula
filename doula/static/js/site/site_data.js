var SiteData = (function() {
    
	// The SiteData Module
	var SiteData = {
	    
	    apps: '',
	    
	    init: function() {
	        this.apps = __apps;
	        
	        console.log(this.apps);
	    }
	    
	    
    };
    // This ends the SiteData module
    
    return SiteData;
})();