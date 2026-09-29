/**
Core script to handle the entire theme and core functions
**/
var DZone = function(){
	/* Search Bar ============ */
	
	/* Load File ============ */
	var dlabTheme = function(){
		 'use strict';
		 var loadingImage = '<img src="images/loading.gif">';
		 jQuery('.dlabload').each(function(){
		 var dlabsrc = $(this).attr('dlabsrc');
		  //jQuery(this).html(loadingImage);
			jQuery(this).hide(function(){
			   jQuery(this).load(dlabsrc, function(){
					jQuery(this).fadeIn('slow');
			   }); 
			})
		 });
		 
		
	}
	
	var dlabTheme1 = function(){
		 'use strict';
		 var loadingImage = '<div class="spinner"><div class="bounce1"></div><div class="bounce2"></div><div class="bounce3"></div></div>';
		 
		 //#dlabdest : Id of container where content will load
		 jQuery('.dlabClickload').on('click', function(event){
			event.preventDefault();
			
			var dlabsrc = $(this).attr('dlabsrc');
			if (typeof dlabsrc !== typeof undefined && dlabsrc !== false) {
				var dlabdest = $(this).attr('dlabdest');
				if (typeof dlabdest !== typeof undefined && dlabdest !== false) {
					jQuery("#"+dlabdest).html(loadingImage);
					setTimeout(function(){ 
						jQuery("#"+dlabdest).load(dlabsrc); 
					}, 500);
				}
				else{
					jQuery(this).html(loadingImage);
					setTimeout(function(){ 
						jQuery(this).load(dlabsrc); 
					},500);
				}
			}

			
		 }); 
		 
	}
	
	/* Function ============ */
	return {
		init:function(){
			dlabTheme();
			dlabTheme1();
		},
	}
	
}();


/* Document.ready Start */	
jQuery(document).ready(function() {
    'use strict';
	DZone.init();
});
/* Document.ready END */

