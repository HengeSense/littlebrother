
var connections_current_page = 0;
var connections_limit = 20;

var urls_current_page = 0;
var urls_limit = 10;

var default_connections_pattern_val = '';
var connections_pattern_timer = undefined;
var connections_pattern = '';
var default_titles_pattern_val = '';
var titles_pattern_timer = undefined;
var titles_pattern = '';
var current_tag = undefined;

(function($) {
	$.fn.makebro = function(bro, bros) {
		var html = $('<span>')
			.addClass('controls');

		if (bros) {
			html.append($('<a>')
				.addClass('broplus_link')
				.attr('href', broplusLink($.extend(bro, { bros : bros })))
				.attr('title', messages.broplus_title)
				.button({
					icons : {
						primary: 'ui-icon-circle-plus'
					},
					text : false
				}));
		}

		html.append($('<a>')
			.addClass('pack_link')
			.attr('href', packLink(bro))
			.attr('title', messages.packlink_title)
			.button({
				icons : {
					primary : 'ui-icon-heart'
				},
				text : false
			}));

		html.addClass('invisible')
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

function showError(node, args) {
	var message = args['message'];

	node
		.html($('<p>')
			.html(message || format(messages.query_error, args)))
		.removeClass()
		.addClass((message && 'centered' || ''))
		.show()
		.blink('#ffc', '#fff');
}

function showQueryError(args) {
	showError($('#errors'), args);
}

function showConnectionsError(args) {
	if (args['status']) {
		showError($('#errors'), args);
		return;
	}

	showError($('#connections_errors'), args);
}

function showUrlsError(args) {
	if (args['status']) {
		showError($('#errors'), args);
		return;
	}

	showError($('#urls_errors'), args);
}

function currentLocation(current_url) {
	var url = window.location.protocol +'//'
		+ window.location.host
		+ window.location.pathname
		+ window.location.search;

	var args = '';

	if (connections_pattern && connections_pattern != default_connections_pattern_val) {
		args += (args && '&' || '') + 'connections=' + connections_pattern;
	}

	if (titles_pattern && titles_pattern != default_titles_pattern_val) {
		args += (args && '&' || '') + 'title=' + titles_pattern;
	}

	if (current_tag) {
		args += (args && '&' || '') + 'tag=' + current_tag;
	}

	if (connections_current_page > 0) {
		args += (args && '&' || '') + 'cpage=' + (connections_current_page + 1);
	}

	if (urls_current_page > 0) {
		args += (args && '&' || '') + 'upage=' + (urls_current_page + 1);
	}

	url += '#' + (args || 'placeholder');

	if (url == current_url + '#placeholder') {
		return current_url;
	}

	return url;
}

function updateLocation() {
	var new_url = currentLocation(window.location.href);

	if (new_url != window.location.href) {
		window.location.href = new_url;
	}
}

function connectionsLoadSuccess(bros) {
	var more_connections_available = (dictSize(bros) >= connections_limit);

	$('#more_connections').button(more_connections_available && 'enable' || 'disable');

	$('#connections_nav').buttonset('enable');
	$('#connections_next').button(more_connections_available && 'enable' || 'disable');
	$('#connections_prev').button(connections_current_page > 0 && 'enable' || 'disable');

	fillConnections(bros);
	updateLocation();
}

function connectionsLoadError(jqXHR) {
	$('#connections_nav').buttonset('enable');

	showConnectionsError({
		status : jqXHR.status
	});
}

function loadConnections(success) {
	$('#connections_nav').buttonset('disable');

	$.bro.connections({
		bros : pageBros('bros'),
		pattern : connections_pattern,
		limit : connections_limit,
		tag : current_tag,
		offset : connections_current_page * connections_limit,
		success : (success || connectionsLoadSuccess),
		error : connectionsLoadError
	});
}

function nextConnections() {
	++connections_current_page;

	reloadConnections();
}

function prevConnections() {
	--connections_current_page;

	if (connections_current_page < 0) {
		connections_current_page = 0;
		return;
	}

	reloadConnections();
}

function reloadConnections(success) {
	$('#broconnections').fadeTo('fast', 0.3);
	loadConnections(success);
}

function updateConnectionsPattern(pattern) {
	if (pattern == connections_pattern) {
		return;
	}

	connections_pattern = (pattern != default_connections_pattern_val && pattern || '');

	reloadConnections();
}

function fillConnections(bros) {
	var connections = $('#broconnections');
	var ul = $('#broconnections > ul');
	if (ul.length == 0) {
		ul = $('<ul>');
		ul.appendTo(connections);
	}

	var replacement_ul = $('<ul>');
	$.each(bros, function (title, args) {
		$('<li>')
			.attr('class', args.tag)
			.append($('<a>')
				.attr('href', profileLink(args))
				.html(title))
			.append($('<span>')
				.attr('class', 'goggles')
				.html('&nbsp;' + args['score']))
			.makebro(args, urlParam('bros'))
			.appendTo(replacement_ul);
	});

	ul.replaceWith(replacement_ul);
	connections.fadeTo('fast', 1);
}

function urlsLoadSuccess(urls) {
	var more_urls_available = (dictSize(urls) >= urls_limit);

	$('#urls_nav').buttonset('enable');
	$('#urls_next').button(more_urls_available && 'enable' || 'disable');
	$('#urls_prev').button(urls_current_page > 0 && 'enable' || 'disable');

	fillUrls(urls);
	updateLocation();
}

function urlsLoadError(jqXHR) {
	$('#urls_nav').buttonset('enable');

	showUrlsError({
		status : jqXHR.status
	});
}

function loadUrls(success) {
	$('#urls_nav').buttonset('disable');

	var titles = titles_pattern;
	var domain = undefined;

	var groups = titles_pattern.match(/site:([^\s]+)?/i);
	if (groups) {
		domain = groups[1]

		if (domain) {
			domain = domain.replace(/^\s+|\s+$/g, '');
		}

		if (domain) {
			var domain_start = titles_pattern.search(groups[0]);
			var domain_stop = domain_start + groups[0].length;

			titles = titles.substr(0, domain_start)
				+ titles.substr(domain_stop, titles.length - domain_stop);
		}
	}

	$.bro.urls({
		bros : pageBros('bros'),
		titles_pattern : titles,
		domain_pattern : domain,
		offset : urls_current_page * urls_limit,
		limit : urls_limit,
		success : (success || urlsLoadSuccess),
		error : urlsLoadError,
	});
}

function nextUrls() {
	++urls_current_page;

	reloadUrls();
}

function prevUrls() {
	--urls_current_page;

	if (urls_current_page < 0) {
		urls_current_page = 0;
		return;
	}

	reloadUrls();
}

function reloadUrls(success) {
	$('#brolinks').fadeTo('fast', 0.3);
	loadUrls(success);
}

function updateTitlesPattern(pattern) {
	if (pattern == titles_pattern) {
		return;
	}

	titles_pattern = (pattern != default_titles_pattern_val && pattern || '');

	reloadUrls();
}

function fillUrls(urls) {
	function shortRef(ref) {
		var max_ref_length = 50; // +3 for ...

		return (ref.length > max_ref_length)
			&& ref.substring(0, max_ref_length) + '...'
			|| ref;
	}

	var links = $('#brolinks');
	var ul = $('#brolinks > ul');
	if (ul.length == 0) {
		ul = $('<ul>');
		ul.appendTo(links);
	}

	var replacement_ul = $('<ul>');
	$.each(urls, function (ref, title) {
		$('<li>')
			.text(title || '')
			.attr('class', 'url_title')
			.appendTo(replacement_ul);

		$('<li>')
			.append($('<a>')
				.attr('href', ref)
				.attr('class', 'url_ref')
				.html(shortRef(ref)))
			.appendTo(replacement_ul);
	})

	ul.replaceWith(replacement_ul);
	links.fadeTo('fast', 1);
}

function updateTag(tag) {
	if (tag == current_tag) {
		return;
	}

	current_tag = tag;
	connections_current_page = 0;

	reloadConnections();
}

function initUrlsPatternBlock() {
	var titles_pattern_input = $('#titles_pattern');

	default_titles_pattern_val = titles_pattern_input.val();
	if (titles_pattern) {
		titles_pattern_input.val(titles_pattern);
	}

	titles_pattern_input
		.focus(function () {
			if (titles_pattern_input.val() == default_titles_pattern_val) {
				titles_pattern_input
					.val('')
					.addClass('query_normal')
					.removeClass('query_default');
			}
		})
		.blur(function () {
			if (titles_pattern_input.val().length == 0) {
				titles_pattern_input
					.val(default_titles_pattern_val)
					.addClass('query_default')
					.removeClass('query_normal');
			}
		})
		.keydown(function () {
			clearTimeout(titles_pattern_timer);
		})
		.keyup(function () {
			clearTimeout(titles_pattern_timer);
			titles_pattern_timer = setTimeout(function () {
				updateTitlesPattern(titles_pattern_input.val());
			}, 500);
		})
		.addClass(titles_pattern_input.val() == default_titles_pattern_val
			&& 'query_default'
			|| 'query_normal')
		.addClass('ui-widget-content ui-widget');
}
/*
function fillFuzzyNames(options) {
	var fuzzy_names = $('#fuzzynames');
	var ul = $('#fuzzynames > ul');
	if (ul.length == 0) {
		ul = $('<ul>');
		ul.appendTo(fuzzy_names);
	}

	var filtered_names = {};
	$.each(options, function (title, args) {
		if ($.inArray(title, pageBros) < 0) {
			filtered_names[title] = args;
		}
	});

	$.each(filtered_names, function (title, args) {
		$('<li>')
			.attr('class', args['tag'])
			.append($('<a>')
				.attr('href', profileLink(title))
				.html(title))
			.append($('<span>')
				.attr('class', 'goggles')
				.html('&nbsp;' + args['score']))
			.appendTo(ul)
	});

	if (dictSize(filtered_names) > 0) {
		$('#fuzzynames_block').show().fadeIn();
	}
}
*/
function initProfileUI() {
	initQueryBlock();

	titles_pattern = urlParam('title');
	connections_pattern = urlParam('connections');
	current_tag = urlParam('tag');
	connections_current_page = Math.max(parseInt(urlParam('cpage') || '1') - 1, 0);
	urls_current_page = Math.max(parseInt(urlParam('upage') || '1') - 1, 0);

	initConnectionsPatternBlock();
	initUrlsPatternBlock();

	var page_bros = pageBros('bros');

	$.each(page_bros, function (index, bro) {
		document.title += (index > 0 && ', ' || '')  + bro.title;
	});

	if (page_bros.length > 1) {
		var names_block = $('#broname');
		$.each(page_bros, function (index, bro) {
			names_block
				.append($('<div>')
					.append($('<a>')
						.attr('href', profileLink(bro))
						.html(bro.title))
					.makebro(bro));

			if (index < page_bros.length - 1) {
				names_block.append(',');
			}
		});
	} else {
		$('#broname')
			.append($('<div>')
				.html(page_bros[0].title)
				.makebro(page_bros[0]));
	}

	$('#fuzzynames_block').hide()

	/*
	if (page_bros.length == 1) {
		$.bro.fuzzyIdents({
			pattern : (page_bros[0].search(' ')
				&& page_bros[0].split(' ')[0]
				|| page_bros[0]),
			success : function(names) {
				fillFuzzyNames(names);
			}
		});
	}
	*/

	reloadConnections(function (bros) {
		connectionsLoadSuccess(bros);
		loadUrls();
	});

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

	$('#connections_type').buttonset();

	$('#connections_prev').button({
		icons : {
			primary : 'ui-icon-triangle-1-w'
		},
		text : false
	})
	.click(function (event) {
		prevConnections();
	});

	$('#connections_next')
		.button({
			icons : {
				primary : 'ui-icon-triangle-1-e'
			},
			text : false
		})
		.click(function (event) {
			nextConnections();
		});

	$('#connections_nav').buttonset();

	$('#urls_prev').button({
		icons : {
			primary : 'ui-icon-triangle-1-w'
		},
		text : false
	})
	.click(function (event) {
		prevUrls();
	});

	$('#urls_next').button({
		icons : {
			primary : 'ui-icon-triangle-1-e'
		},
		text : false
	})
	.click(function (event) {
		nextUrls();
	});

	$('#urls_nav').buttonset();
}
