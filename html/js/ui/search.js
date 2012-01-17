
(function($) {
	$.fn.makebro = function(args) {
		var title = args.title || '';
		var tag = args.tag || '';

		var html = $('<span>')
			.addClass('controls')
			.append($('<a>')
				.addClass('pack_link')
				.attr('href', packLink(args))
				.attr('title', 'Перейти к стае')
				.button({
					icons : {
						primary : 'ui-icon-heart'
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

function showSearchError(args) {
	showError(args);
}

function entriesLoadSuccess(entries) {
	var more_entries_available = (dictSize(entries) >= settings.search.entries);

	fillEntries(entries);

	$('#entries_prev').button(parseInt(urlParam('epage')) > 1 && 'enable' || 'disable');
	$('#entries_next').button(more_entries_available && 'enable' || 'disable');
}

function entriesLoadError(jqXHR) {
	$('#entries_prev').button(parseInt(urlParam('epage')) > 1 && 'enable' || 'disable');
	$('#entries_next').button('enable');

	showSearchError(jqXHR);
}

function updatePage(oldurl, newurl) {
	var old_page = oldurl && (urlParam('epage', oldurl) || 1) || -1;
	var new_page = newurl && (urlParam('epage', newurl) || 1) || -1;

	if (old_page != new_page) {
		reloadEntries(entriesLoadSuccess);
	}

	var current_href = window.location.href;
	$(window).unbind('hashchange').bind('hashchange', function(args) {
		updatePage(current_href, window.location.href);
	});
}

function loadEntries(success) {
	$('#entries_prev').button('disable');
	$('#entries_next').button('disable');

	$.bro.idents({
		pattern : urlParam('q'),
		offset : parseInt(urlParam('epage')) * settings.search.entries,
		limit : settings.search.entries,
		success : (success || entriesLoadSuccess),
		error : entriesLoadError
	});
}

function reloadEntries(success) {
	$('#entries').fadeTo('fast', 0.3);
	loadEntries(success);
}

function fillEntries(bros) {
	var entries = $('#entries');
	var ul = $('#entries > ul');
	if (ul.length == 0) {
		ul = $('<ul>');
		ul.appendTo(entries);
	}

	var replacement_ul = $('<ul>');
	$.each(bros, function (title, args) {
		$('<li>')
			.attr('class', args['tag'])
			.append($('<a>')
				.attr('href', profileLink(args))
				.html(title))
			.append($('<span>')
				.attr('class', 'goggles')
				.html('&nbsp;' + args['score']))
			.makebro(args)
			.appendTo(replacement_ul);
	});

	ul.replaceWith(replacement_ul);
	entries.fadeTo('fast', 1);
}

function navigateToPage(page) {
	if (page < 1) {
		return;
	}

	var url = window.location.protocol +'//'
	+ window.location.host
	+ window.location.pathname
	+ window.location.search;

	if (page < 2) {
		url += '#';
	} else {
		url += '#epage=' + page;
	}

	if (window.location.href != url) {
		window.location.href = url;
	}
}

function initSearchUI() {
	initQueryBlock();

	$('#entries_prev').button({
		icons : {
			primary : 'ui-icon-triangle-1-w'
		},
		text : false
	})
	.click(function (event) {
		navigateToPage(parseInt(urlParam('epage') || 1) - 1);
	});

	$('#entries_next').button({
		icons : {
			primary : 'ui-icon-triangle-1-e'
		},
		text : false
	})
	.click(function (event) {
		navigateToPage(parseInt(urlParam('epage') || 1) + 1);
	});

	updatePage(null, window.location.href);
}
