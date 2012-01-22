
function showQueryError(args) {
	var message = args['message'];

	showError({
		message : message || format(messages.query_error, args),
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
			$('#total_urls').html(total_urls || '0');
			$('#total_records').html(total_records || '0');
			$('#top_name').append($('<a>')
				.attr('href', profileLink({ title : top_name, tag : 'names' }))
				.html(top_name || ''));
			$('#bottom_name').append($('<a>')
				.attr('href', profileLink({ title: bottom_name, tag : 'names' }))
				.html(bottom_name || ''));
			$('#top_org').append($('<a>')
				.attr('href', profileLink({ title : top_org, tag : 'orgs' }))
				.html(top_org || ''));
			$('#bottom_org').append($('<a>')
				.attr('href', profileLink({ title : bottom_org, tag : 'orgs' }))
				.html(bottom_org || ''));
		},
		error : function (jqXHR) {
			showError({
				message : format(messages.general_failure, {
					status : jqXHR.status
				})
			});
		}
	});

	$('#privacy')
		.hide();

	$('#privacy_anchor')
		.click(function (event) {
			event.preventDefault();
			event.stopPropagation();

			if (!$('#privacy').is(':visible')) {
				$('#privacy').slideDown();
			} else {
				$('#privacy').slideUp();
			}
		});
}
