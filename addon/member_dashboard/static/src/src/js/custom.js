function readURL(input, id) {
    if (input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            document.getElementById(id).src = e.target.result;
        }

        reader.readAsDataURL(input.files[0]);
    }
}
var checkList2 = document.getElementById('list2');
checkList2.getElementsByClassName('anchor')[0].onclick = function(evt) {
    if (checkList2.classList.contains('visible'))
      checkList2.classList.remove('visible');
    else
      checkList2.classList.add('visible');
  }

var checkList = document.getElementById('list1');
checkList.getElementsByClassName('anchor')[0].onclick = function(evt) {
  if (checkList.classList.contains('visible'))
    checkList.classList.remove('visible');
  else
    checkList.classList.add('visible');
}



const checked = document.querySelectorAll('input[type="checkbox"]:checked');
console.log([...checked].map(c => c.value))


//mentor registartation

$(document).ready(function(){
    
  var current_fs, next_fs, previous_fs; //fieldsets
  var opacity;
  var current = 1;
  var steps = $("fieldset").length;
  
  setProgressBar(current);
  
  $(".next").click(function(){
      
      current_fs = $(this).parent();
      next_fs = $(this).parent().next();
      
      //Add Class Active
      $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");
      
      //show the next fieldset
      next_fs.show(); 
      //hide the current fieldset with style
      current_fs.animate({opacity: 0}, {
          step: function(now) {
              // for making fielset appear animation
              opacity = 1 - now;
  
              current_fs.css({
                  'display': 'none',
                  'position': 'relative'
              });
              next_fs.css({'opacity': opacity});
          }, 
          duration: 500
      });
      setProgressBar(++current);
  });
  
  $(".previous").click(function(){
      
      current_fs = $(this).parent();
      previous_fs = $(this).parent().prev();
      
      //Remove class active
      $("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");
      
      //show the previous fieldset
      previous_fs.show();
  
      //hide the current fieldset with style
      current_fs.animate({opacity: 0}, {
          step: function(now) {
              // for making fielset appear animation
              opacity = 1 - now;
  
              current_fs.css({
                  'display': 'none',
                  'position': 'relative'
              });
              previous_fs.css({'opacity': opacity});
          }, 
          duration: 500
      });
      setProgressBar(--current);
  });
  
  function setProgressBar(curStep){
      var percent = parseFloat(100 / steps) * curStep;
      percent = percent.toFixed();
      $(".progress-bar")
        .css("width",percent+"%")   
  }
  
  $(".submit").click(function(){
      return false;
  })
      
  });

// Membership signup
var nxt_btn=document.querySelectorAll(".membership_next_button");
var prev_btn=document.querySelectorAll(".previous_button");
var submit_btn=document.querySelectorAll(".submit_button");
var main_form=document.querySelectorAll(".main");
var main_signin_form=document.querySelectorAll(".main_signin");
var sign_in_submit=document.querySelector(".membership_sign_next_button")
var progressbar = document.querySelectorAll(".steps li");
var steps = document.querySelector(".steps");
let forumnumber=0;
nxt_btn.forEach(function(butn){
  butn.addEventListener('click',function(){
      if(!validateform()){
          return false;
      }
      forumnumber++;
      progress('color');
      update_form(); 
  });
});  


prev_btn.forEach(function(prev_button){
    prev_button.addEventListener('click',function(){ 
      forumnumber--;
      progress('nocolor');
      update_form();
    });
}); 

submit_btn.forEach(function(submit_button){
    submit_button.addEventListener('click',function(){
        if(!validateform()){
            return false;
        }
    var f_name=document.querySelector("#user_name");
    var shown_name = document.querySelector("#shown_name");
    shown_name.innerHTML=f_name.value;
        forumnumber++;
        update_form();
        steps.classList.add("d-none");
    });
});

    let signinnumber = 0;
    sign_in_submit.addEventListener('click',function(){
        if(!validateformsignin()) return false;
        signinnumber++;
        main_signin_form.forEach(function(main){
            main.classList.remove("active");
        });
        var f_name=document.querySelector("#user_signin_name");
        var shown_name = document.querySelector("#shown_signin_name");
        shown_name.innerHTML=f_name.value;
        main_signin_form[signinnumber].classList.add("active");
    });

 
   
 
 function progress(state){ 
     if(state=='color'){
          progressbar[forumnumber].classList.add('li-active'); 
     }else{
         
         progressbar[forumnumber+1].classList.remove('li-active');
     }
    
 }


function update_form(){ 
    main_form.forEach(function(main){
      main.classList.remove('active');
    }); 
      main_form[forumnumber].classList.add('active');   
}
  
function validateform(){  
    validate=true;
var validate_inputs = document.querySelectorAll(".main.active input");
validate_inputs.forEach(function(input_valid){
    input_valid.classList.remove('warning'); 
    if(input_valid.hasAttribute('require')){ 
        if(input_valid.value.length==0){
            validate=false;
            input_valid.classList.add('warning');
        }
    }
});
return validate;
}

function validateformsignin(){  
    validate=true;
var validate_inputs = document.querySelectorAll(".main_signin.active input");
validate_inputs.forEach(function(input_valid){
    input_valid.classList.remove('warning'); 
    if(input_valid.hasAttribute('require')){ 
        if(input_valid.value.length==0){
            validate=false;
              input_valid.classList.add('warning');
        }
    }
});
return validate;
}


var signin_toggle = document.querySelector(".sign-in-up-toggle");
var s_form = document.querySelectorAll(".s_form");
var account = document.querySelectorAll(".account");
var right_image=document.querySelectorAll(".right_img");
signin_toggle.addEventListener('click',function(){
       
      s_form.forEach(function(form){
          form.classList.toggle("d-none");
      });
       
        account.forEach(function(acc){
          acc.classList.toggle("d-none");
      });
        
        right_image.forEach(function(ri_img){
          ri_img.classList.toggle("d-none");  
        });
        
      if(signin_toggle.innerHTML=="Sign in"){
          signin_toggle.innerHTML="Sign up";
      }
      else{
          signin_toggle.innerHTML="Sign in";
      }
     
      
});




//donation js

var check_it=document.querySelector(".check_it");
check_it.onclick=function(){
check_it.classList.toggle('green');
}

// (function ($) {
	
// 	"use strict";

// 	// Header Type = Fixed
//   $(window).scroll(function() {
//     var scroll = $(window).scrollTop();
//     var box = $('.header-text').height();
//     var header = $('header').height();

//     if (scroll >= box - header) {
//       $("header").addClass("background-header");
//     } else {
//       $("header").removeClass("background-header");
//     }
//   });


// 	$('.owl-banner').owlCarousel({
// 		items:1,
// 		loop:true,
// 		dots: true,
// 		nav: false,
// 		autoplay: true,
// 		margin:0,
// 		  responsive:{
// 			  0:{
// 				  items:1
// 			  },
// 			  600:{
// 				  items:1
// 			  },
// 			  1000:{
// 				  items:1
// 			  },
// 			  1600:{
// 				  items:1
// 			  }
// 		  }
// 	})

//     $('.owl-services').owlCarousel({
//         items:4,
//         loop:true,
//         dots: true,
//         nav: false,
//         autoplay: true,
//         margin:5,
//           responsive:{
//               0:{
//                   items:1
//               },
//               600:{
//                   items:2
//               },
//               1000:{
//                   items:3
//               },
//               1600:{
//                   items:4
//               }
//           }
//     })

//     $('.owl-portfolio').owlCarousel({
//         items:4,
//         loop:true,
//         dots: true,
//         nav: true,
//         autoplay: true,
//         margin:30,
//           responsive:{
//               0:{
//                   items:1
//               },
//               700:{
//                   items:2
//               },
//               1000:{
//                   items:3
//               },
//               1600:{
//                   items:4
//               }
//           }
//     })

    

// 	// Menu Dropdown Toggle
//   if($('.menu-trigger').length){
//     $(".menu-trigger").on('click', function() { 
//       $(this).toggleClass('active');
//       $('.header-area .nav').slideToggle(200);
//     });
//   }


//   // Menu elevator animation
//   $('.scroll-to-section a[href*=\\#]:not([href=\\#])').on('click', function() {
//     if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
//       var target = $(this.hash);
//       target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
//       if (target.length) {
//         var width = $(window).width();
//         if(width < 991) {
//           $('.menu-trigger').removeClass('active');
//           $('.header-area .nav').slideUp(200);  
//         }       
//         $('html,body').animate({
//           scrollTop: (target.offset().top) + 1
//         }, 700);
//         return false;
//       }
//     }
//   });

//   $(document).ready(function () {
//       $(document).on("scroll", onScroll);
      
//       //smoothscroll
//       $('.scroll-to-section a[href^="#"]').on('click', function (e) {
//           e.preventDefault();
//           $(document).off("scroll");
          
//           $('.scroll-to-section a').each(function () {
//               $(this).removeClass('active');
//           })
//           $(this).addClass('active');
        
//           var target = this.hash,
//           menu = target;
//           var target = $(this.hash);
//           $('html, body').stop().animate({
//               scrollTop: (target.offset().top) + 1
//           }, 500, 'swing', function () {
//               window.location.hash = target;
//               $(document).on("scroll", onScroll);
//           });
//       });
//   });

//   function onScroll(event){
//       var scrollPos = $(document).scrollTop();
//       $('.nav a').each(function () {
//           var currLink = $(this);
//           var refElement = $(currLink.attr("href"));
//           if (refElement.position().top <= scrollPos && refElement.position().top + refElement.height() > scrollPos) {
//               $('.nav ul li a').removeClass("active");
//               currLink.addClass("active");
//           }
//           else{
//               currLink.removeClass("active");
//           }
//       });
//   }



// 	// Page loading animation
// 	 $(window).on('load', function() {

//         $('#js-preloader').addClass('loaded');

//     });

	

// 	// Window Resize Mobile Menu Fix
//   function mobileNav() {
//     var width = $(window).width();
//     $('.submenu').on('click', function() {
//       if(width < 767) {
//         $('.submenu ul').removeClass('active');
//         $(this).find('ul').toggleClass('active');
//       }
//     });
//   }




// })(window.jQuery);