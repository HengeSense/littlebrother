
function showQueryError(args) {
	var message = args['message'];
	
	showError({
		message : message || format(query_error, args),
		style : (message && 'centered' || '')
	});
}

function showError(args) {
	var message = args['message'] || '';
	
	if (!message) {
		return;
	}
	
	var style = args['style'];
	
	$('#errors')
		.html($('<p>')
			.html(message))
		.removeClass()
		.addClass(style)
		.show()
		.blink('#ffc', '#fff');
}

function initIndexUI() {
	initQueryBlock();
	
	$.bro.stats({
		success : function fill_stats(stats) {
			var total_idents = stats['total_idents'];
			var total_names = stats['total_names'];
			var total_orgs = stats['total_orgs'];
			var top_ident = stats['top_ident'];
			var bottom_ident = stats['bottom_ident'];
			var total_urls = stats['total_urls'];
			var total_records = stats['total_records'];
			var top_name = stats['top_name'];
			var bottom_name = stats['bottom_name'];
			var top_org = stats['top_org'];
			var bottom_org = stats['bottom_org'];
			
			$('#total_idents').html(total_idents || '0');
			$('#total_names').html(total_names || '0');
			$('#total_orgs').html(total_orgs || '0');
			$('#top_ident').append($('<a>')
				.attr('href', profileLink(top_ident))
				.html(top_ident || ''));
			$('#bottom_ident').append($('<a>')
				.attr('href', profileLink(bottom_ident))
				.html(bottom_ident || ''));
			$('#total_urls').html(total_urls || '0');
			$('#total_records').html(total_records || '0');
			$('#top_name').append($('<a>')
				.attr('href', profileLink(top_name))
				.html(top_name || ''));
			$('#bottom_name').append($('<a>')
				.attr('href', profileLink(bottom_name))
				.html(bottom_name || ''));
			$('#top_org').append($('<a>')
				.attr('href', profileLink(top_org))
				.html(top_org || ''));
			$('#bottom_org').append($('<a>')
				.attr('href', profileLink(bottom_org))
				.html(bottom_org || ''));
		}, 
		error : function (jqXHR) {
			showError({
				message : format(general_failure, {
					status : jqXHR.status
				})
			});
		}
	});
	
	$('#privacy')
		.hide();
	
	$('#info_block')
		.append(
			$('<a>')
				.attr('href', '/')
				.text('Privacy')
				.click(function (event) {
					event.preventDefault();
					event.stopPropagation();
					
					$(this).hide();
					$('#privacy').slideDown();
				}));
}
