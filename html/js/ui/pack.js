
var current_tag = undefined;
var current_level = undefined;
var default_connections_pattern_val = '';
var connections_pattern_timer = undefined;
var connections_pattern = '';

(function($) {
	$.fn.broCloud = function(cloud, scale) {

		var outer = $('<div>');
		$.each(cloud, function (ident, args) {
			var title = args['title'] || '';
			var weight = args['weight'] || '';
			var tag = args['tag'] || '';
			var level = args['level'] || '';

			var span = $('<span>')
				.addClass(tag)
				.addClass('leaf')
				.addClass('lv' + level)
				.addClass('s' + scale(weight))
				.append($('<a>')
					.attr('href', packLink(args))
					.html(title))
				.append($('<span>')
					.attr('class', 'goggles')
					.html('&nbsp;' + weight))
				.append($('<span>')
					.attr('class', 'goggles')
					.html('&nbsp;lv' + level))
				.append(' '); // renderer breaks line on whitespaces and don't on </span>. i fucking hate him

			span
				.makebro(title)
				.appendTo(outer);
		});

		$(this).html('');
		outer.appendTo($(this));

		return $(this);
	};

	$.fn.makebro = function(args) {
		var html = $('<span>')
			.addClass('controls')
			.append($('<a>')
				.addClass('profile_link')
				.attr('href', profileLink(args))
				.attr('title', messages.profilelink_title)
				.button({
					icons : {
						primary: "ui-icon-person"
					},
					text : false
				}))
			.addClass('invisible')
			.prependTo($(this));

		$(this).mouseenter(function (event) {
			html.removeClass('invisible');
		});

		$(this).mouseleave(function (event) {
			html.addClass('invisible');
		});

		return $(this);
	}
})(jQuery);

function showError(args) {
	var message = args['message'];

	$('#errors')
		.html($('<p>')
			.html(message || format(messages.query_error, args)))
		.removeClass()
		.addClass((message && 'centered' || ''))
		.show()
		.blink('#ffc', '#fff');
}

function showQueryError(args) {
	showError(args);
}

function showPackError(args) {
	showError(args);
}

function currentUrl(current_url) {
	var url = window.location.protocol +'//'
		+ window.location.host
		+ window.location.pathname
		+ window.location.search;

	var args = '';

	if (current_tag) {
		args += (args && '&' || '') + 'tag=' + current_tag;
	}

	if (current_level) {
		args += (args && '&' || '') + 'level=' + current_level;
	}

	if (connections_pattern) {
		args += (args && '&' || '') + 'connections=' + connections_pattern;
	}

	url += '#' + (args || 'placeholder');

	if (url == current_url + '#placeholder') {
		return current_url;
	}

	return url;
}

function updateLocation() {
	var new_url = currentUrl(window.location.href);

	if (new_url != window.location.href) {
		window.location.href = new_url;
	}
}

function updateConnectionsPattern(pattern) {
	if (pattern == connections_pattern) {
		return;
	}

	connections_pattern = (pattern != default_connections_pattern_val && pattern || '');

	updateLocation();
	reloadPack();
}

function packLoadSuccess(bros) {
	fillPack(bros);
}

function packLoadError(jqXHR) {
	showPackError({
		status : jqXHR.status
	});
}

function loadPack(success) {
	$.bro.pack({
		bro : pageBros('bro')[0],
		tags : (current_tag && [ current_tag ] || settings.query.nofilter_tags),
		pattern : connections_pattern,
		success : (success || packLoadSuccess),
		error : packLoadError
	});
}

function reloadPack(success){
	$('#bropack').fadeTo('fast', 0.3);

	loadPack(success);
}

function updateTag(tag) {
	if (tag == current_tag) {
		return;
	}

	current_tag = tag;

	reloadPack();
	updateLocation();
}

function styleLevel(level) {
	if (level) {
		$('#bropack > * > span:not(.lv' + level + ')')
			.addClass('hidden_level')
			.removeClass('front');

		$('#bropack > * > span:.lv' + level)
			.removeClass('hidden_level')
			.addClass('front');
	}
	else {
		$('#bropack > * > span')
			.removeClass('hidden_level')
			.removeClass('front');
	}
}

function updateLevel(level) {
	if (level == current_level) {
		return;
	}

	current_level = level;

	styleLevel(current_level);
	updateLocation();
}

function fillPack(bros) {
	var names = $('#bropack');

	var min_score = undefined;
	var max_score = undefined;

	var cloud = [];
	$.each(bros, function (title, args) {
		var score = parseFloat(args['score']);

		if (min_score == undefined || score < min_score) {
			min_score = score;
		}

		if (max_score == undefined || score > max_score) {
			max_score = score;
		}

		cloud.push({
			'title' : title,
			'weight' : score,
			'level' : parseInt(args['level']),
			'tag' : args['tag'],
		});
	});

	var range = max_score - min_score;

	names
		.broCloud(cloud, function (weight) {
			return Math.ceil((weight - min_score) / (range / 9)) + 1;
		});

	styleLevel(current_level);

	names.fadeTo('fast', 1);
}

function initPackUI() {
	initQueryBlock();

	current_tag = urlParam('tag') || '';
	current_level = parseInt(urlParam('level')) || 0;
	connections_pattern = urlParam('connections') || '';

	initConnectionsPatternBlock();

	page_bros = pageBros('bro');

	document.title += page_bros[0].title;

	$('#broname')
		.append($('<div>')
			.html(page_bros[0].title)
			.makebro(page_bros[0]));

	$('#show_names')
		.attr('checked', current_tag == 'names')
		.click(function (event) {
			updateTag('names');
		});

	$('#show_orgs')
		.attr('checked', current_tag == 'orgs')
		.click(function (event) {
			updateTag('orgs');
		});

	$('#show_all')
		.attr('checked', !current_tag)
		.click(function (event) {
			updateTag('');
		});

	$('#level_1')
		.attr('checked', current_level == 1)
		.click(function (event) {
			updateLevel(1);
		});

	$('#level_2')
		.attr('checked', current_level == 2)
		.click(function (event) {
			updateLevel(2);
		});

	$('#level_all')
		.attr('checked', !current_level)
		.click(function (event) {
			updateLevel('');
		});

	$('#connections_type').buttonset();
	$('#level_num').buttonset();

	loadPack();
}
