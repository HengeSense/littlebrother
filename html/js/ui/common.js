
(function($) {
	$.fn.blink = function(from_color, to_color, duration) {
		if (!duration) {
			duration = 600;
		}
		
		$(this)
			.css('background-color', from_color)
			.animate({
				backgroundColor: to_color 
			}, duration);
	}
})(jQuery);

dictSize = function(obj) {
    var size = 0, key;
    
    for (key in obj) {
        if (obj.hasOwnProperty(key)) {
        	size++;
        }
    }
    
    return size;
}

function prepareNameForUrl(name) {
	return name.replace(/\s+/g, '+')
}

function urlParam(name) {
	var results = new RegExp('[\\?&#]' + name + '=([^&#]*)').exec(window.location.href);
	
	if (!results) { 
		return ''; 
	}
	
	return decodeURI(results[1].replace(/\+/g, ' '));
}

function profileLink(title) {
	return '/profile.html?bros=' + title.replace(/\s/g, '+');
}

function broplusLink(title, bros) {
	return (bros && ('/profile.html?bros=' + (bros.join(',') + ',' + title).replace(/\s/g, '+')) || null);
}

function packLink(title) {
	return '/pack.html?bro=' + title.replace(/\s/g, '+');
}

function initConnectionsPatternBlock() {
	var input = $('#connections_pattern');
	
	default_connections_pattern_val = input.val();
	if (connections_pattern) {
		input.val(connections_pattern);
	}
	
	input
		.focus(function () {
			if (input.val() == default_connections_pattern_val) {
				input
					.val('')
					.addClass('query_normal')
					.removeClass('query_default');
			}
		})
		.blur(function () {
			if (input.val().length == 0) {
				input
					.val(default_connections_pattern_val)
					.addClass('query_default')
					.removeClass('query_normal');
			}
		})
		.keydown(function () {
			clearTimeout(connections_pattern_timer);
		})
		.keyup(function () {
			clearTimeout(connections_pattern_timer);
			connections_pattern_timer = setTimeout(function () {
				updateConnectionsPattern(input.val());
			}, 500);
		})
		.addClass(input.val() == default_connections_pattern_val && 'query_default' || 'query_normal')
		.addClass('ui-widget-content ui-widget');
}
