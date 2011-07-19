
var entries_current_page = 0;
var entries_limit = 5;
var search_pattern = '';

(function($) {
	$.fn.makebro = function(title, bros) {
		var html = $('<span>')
			.addClass('controls')
			.append($('<a>')
				.addClass('pack_link')
				.attr('href', packLink(title))
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
			.html(message || format(page_error, args)))
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

function currentLocation(current_url) {
	var url = window.location.protocol +'//' 
		+ window.location.host 
		+ window.location.pathname 
		+ window.location.search;
	
	var args = '';
	
	if (entries_current_page > 0) {
		args += (args && '&' || '') + 'epage=' + (entries_current_page + 1);
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

function entriesLoadSuccess(entries) {
	var more_entries_available = (dictSize(entries) >= entries_limit);
	
	fillEntries(entries);
	
	$('#entries_prev').button(entries_current_page > 0 && 'enable' || 'disable');
	$('#entries_next').button(more_entries_available && 'enable' || 'disable');
}

function entriesLoadError(jqXHR) {
	$('#entries_prev').button(entries_current_page > 0 && 'enable' || 'disable');
	$('#entries_next').button('enable');
	
	showSearchError(jqXHR);
}

function loadEntries(success) {
	$('#entries_prev').button('disable');
	$('#entries_next').button('disable');
	
	$.bro.idents({
		pattern : search_pattern, 
		offset : entries_current_page * entries_limit, 
		success : (success || entriesLoadSuccess), 
		error : entriesLoadError
	});
	
	updateLocation();
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
				.attr('href', profileLink(title))
				.html(title))
			.append($('<span>')
				.attr('class', 'goggles')
				.html('&nbsp;' + args['score']))
			.makebro(title)
			.appendTo(replacement_ul);
	});
	
	ul.replaceWith(replacement_ul);
	entries.fadeTo('fast', 1);
}

function prevEntries() {
	--entries_current_page;
	
	if (entries_current_page < 0) {
		entries_current_page = 0;
		return;
	}
	
	reloadEntries();
}

function nextEntries() {
	++entries_current_page;
	
	reloadEntries();
}

function initSearchUI() {
	initQueryBlock();
	
	search_pattern = urlParam('search');
	entries_current_page = Math.max(parseInt(urlParam('epage') || '1') - 1, 0);
	
	$('#entries_prev').button({
		icons : {
			primary : 'ui-icon-triangle-1-w'
		}, 
		text : false
	})
	.click(function (event) {
		prevEntries();
	});
	
	$('#entries_next').button({
		icons : {
			primary : 'ui-icon-triangle-1-e'
		}, 
		text : false
	})
	.click(function (event) {
		nextEntries();
	});
	
	loadEntries();
	updateLocation();
}
