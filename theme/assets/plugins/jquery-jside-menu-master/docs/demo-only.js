/*  Author: Asif Mughal
 *   URL: https://www.codehim.com
 *   License: MIT License
 *   Copyright (c) 2018 - Asif Mughal
 */
/* File: demo-only.js */
$(function(){
/* Demo only */
var jSide = $(".left-sidemenu .bg-color");
$(".menu-position").on('change', function(){ $(jSide).not(".bg-color").addClass($(this).val()); 
$(".j-pos").html('jSidePosition: "position-right",');
if($(this).val() == 'position-left'){
$(jSide).removeClass("position-right");
$(".j-pos").html('jSidePosition: "position-left",');
$(".menu-trigger").removeClass("right").addClass("left");} else {
$(jSide).removeClass("position-left"); $(".menu-trigger").removeClass("left").addClass("right");}});
$(".bg-color").on('change', function(){var color = $(this).val();
$(jSide).css({'background' : color,});
$(".bg-color-input").val(color);});
$(".bg-color-input").on('input', function(){
$(jSide).css({'background' : $(this).val(),});});$("#set-top").change(function(){
$(".bg-color").addClass("sticky");
$(".j-sticky").html("jSideSticky: true,");
});
$("#set-st").change(function(){
$(".bg-color").removeClass("sticky");
$(".j-sticky").html("jSideSticky: false,");});
$(".theme-tray span").click(function() {
var skin = $(this).attr("class");
$(".bg-color").attr('class', skin).addClass("bg-color sticky");
$(".left-sidemenu").attr('class', skin).addClass("left-sidemenu position-left");
var newcode = 'jSideSkin:'+'\"'+skin+'\",';
$(".j-skin").html(newcode);
});
});