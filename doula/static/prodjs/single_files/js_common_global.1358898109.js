$(document).ready(function(){$.each($('img.gravatar'),function(){if(this.naturalWidth===0||this.naturalHeight===0||this.complete===false){$(this).attr('src','/images/anon-gravatar.png');}});setTimeout(function(){$('[rel="popover"]').popover();$('[rel="tooltip"]').tooltip();},500);setSideTab=function(){var st=$('.side_tab');var cnt=$('.content');st.css({'left':cnt.position().left+cnt.width()+st.width()});};setTimeout(setSideTab,500);$(window).on('resize',function(){setSideTab();});if(document.location.href.match(/docs/)){var sideBarEl=$('#docs-sidebar');var ogTop=sideBarEl.offset().top;scrollSideTab=function(){var scrollTop=window.pageYOffset||document.documentElement.scrollTop||document.body.scrollTop;if(scrollTop>=ogTop){var scrollTop=scrollTop-ogTop+7+'px';sideBarEl.css('marginTop',scrollTop);}
else{scrollTop-7+'px';sideBarEl.css('marginTop',scrollTop);}}
$(window).on('scroll',scrollSideTab);}});