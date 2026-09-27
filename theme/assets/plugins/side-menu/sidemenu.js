(function () {
	"use strict";

	var slideMenu = $('.side-menu');
	$('.app').addClass('sidebar-mini');
	
	// Toggle Sidebar
	$(document).on("click", "[data-toggle='sidebar']", function(event) {
		event.preventDefault();
		$('.app').toggleClass('sidenav-toggled');
		$('.app').removeClass('sidenav-toggled4');
	});
	$(document).on("click", ".sidenav-toggled .app-sidebar__toggle", function(event) {
		event.preventDefault();
		$('.app').toggleClass('sidenav-toggled1');
	});
	$(document).on("click", ".sidenav-toggled .resp-tab-item", function(event) {
		event.preventDefault();
		$('.app').addClass('sidenav-toggled4');
		$('.app').removeClass('sidenav-toggled1');
		$('.app').removeClass('sidenav-toggled');
	});
	
	//mobile  Toggle Sidebar
	if ( $(window).width() < 767) { 
		$(document).on("click", "[data-toggle='sidebar']", function(event) {
			event.preventDefault();
			$('.app').toggleClass('sidenav-mobile');
		});
		
		$(document).on("click", ".sidenav-mobile .resp-tab-item", function(event) {
			event.preventDefault();
			$('.app').toggleClass('sidenav-toggled1');
			$('.app').toggleClass('sidenav-toggled');
		});
	}
	$(document).on("click", "[data-toggle='slide']", function(event) {
		event.preventDefault();
		if(!$(this).parent().hasClass('is-expanded')) {
			slideMenu.find("[data-toggle='slide']").parent().removeClass('is-expanded');
		}
		$(this).parent().toggleClass('is-expanded');
	});
	
	$(document).on("click", "[data-toggle='slide1']", function(event) {
		event.preventDefault();
		if(!$(this).parent().hasClass('is-expanded1')) {
			slideMenu.find("[data-toggle='slide1']").parent().removeClass('is-expanded1');
		}
		$(this).parent().toggleClass('is-expanded1');
	});

	// Set initial active toggle
	$("[data-toggle='slide.'].is-expanded").parent().toggleClass('is-expanded');

	//Activate bootstrip tooltips
	$("[data-toggle='tooltip']").tooltip();
	
	//Automatic reloaded Page
	/* var context;
	var $window = $(window);
	if ($window.width() < 739) {
		context = 'small';
	} 
	$(window).on("resize",function(e) {
		if(($window.width() < 739)) {
			location.reload();
		} 
	}); */
})();
