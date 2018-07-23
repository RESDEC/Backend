
    var $j = jQuery.noConflict();
	var $window = $j(window);		//Window object
	var scrollTime = 0.6;			//Scroll time
	var scrollDistance = 400;		//Distance. Use smaller value for shorter scroll and greater value for longer scroll

    mobile_ie = -1 !== navigator.userAgent.indexOf("IEMobile");

    if (!$j('html').hasClass('touch') && !mobile_ie) {
        $window.on("mousewheel DOMMouseScroll", function (event) {

            event.preventDefault();

            var delta = event.originalEvent.wheelDelta / 120 || -event.originalEvent.detail / 3;
            var scrollTop = $window.scrollTop();
            var finalScroll = scrollTop - parseInt(delta * scrollDistance);

            TweenLite.to($window, scrollTime, {
                scrollTo: {
                    y: finalScroll, autoKill: !0
                },
                ease: Power1.easeOut,
                autoKill: !0,
                overwrite: 5
            });

        });
    }
	
