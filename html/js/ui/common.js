
(function($) {
	$.fn.blink = function(from_color, to_color, duration) {
		if (!duration) {
			duration = 600;
		}

		if (!to_color) {
			to_color = $('body').css('background-color');
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

function nameForUrl(args) {
	var title = args.title || '';
	var tag = args.tag || '';

	return title.replace(/\s+/g, '+') + ':' + tag;
}

function nameFromUrl(str) {
	var matches = str.match(/(.*):(.*)/); // greedy
	if (matches) {
		var name = {};
		name.title = matches[1].split('+').join(' ');
		name.tag = matches[2];

		return name;
	}
}

function urlParam(name, href) {
	var url = href || window.location.href;
	var args = $.extend($.deparam.querystring(url), $.deparam.fragment(url))

	return args[name];
}

function fragmentParam(name, href) {
	var url = href || window.location.href;
	return $.deparam.fragment(url)[name];
}

function replaceUrlParam(name, value, href) {
	var url = href || window.location.href;
	return $.param.querystring(url, name + '=' + value);
}

function replaceFragmentParam(name, value, href) {
	var url = href || window.location.href;
	return $.param.fragment(url, name + '=' + value);
}

function pageBros(tag) {
	var bros = [];
	var page_bros = urlParam(tag).split(',');

	for (var i in page_bros) {
		bros.push(nameFromUrl(page_bros[i]));
	}

	return bros;
}

function profileLink(args) {
	return '/profile.html?bros=' + nameForUrl(args);
}

function broplusLink(args) {
	var bros = args.bros || '';

	return '/profile.html?bros=' + (bros && bros + ',' || '') + nameForUrl(args);
}

function packLink(args) {
	return '/pack.html?bro=' + nameForUrl(args);
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
