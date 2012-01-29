
var default_input_val = '';

function directQuery(ident, ident_tags) {
	$.bro.idents({
		pattern : ident,
		tags : ident_tags,
		success : function (bros) {
			switch (dictSize(bros)) {
			case 0:
				showQueryError({
					message : messages.not_found
				});
				break;

			case 1:
				for (key in bros) {
			        if (bros.hasOwnProperty(key)) {
			        	var bro = bros[key];

			        	window.location = ('/profile.html?bros='
			        		+ nameForUrl({ title : bro.title, tag : bro.tag }));
			        	break;
			        }
				}
				break;

			default:
				window.location = ('/search.html?q=' + ident);
			}
		},
		error : function (jqXHR) {
			showQueryError({
				status : jqXHR.status,
			});
		}
	});
}

function initQueryBlock() {
	var input = $('#query');

	default_input_val = input.val();

	input
		.val(default_input_val)
		.focus(function () {
			if (input.val() == default_input_val) {
				input
					.val('')
					.addClass('query_normal')
					.removeClass('query_default');
			}
		})
		.blur(function () {
			if (input.val().length == 0) {
				input
					.val(default_input_val)
					.addClass('query_default')
					.removeClass('query_normal');
			}
		})
		.autocomplete({
			source : function(req, callback) {
				input.addClass('input_loading');

				$.bro.idents({
					pattern : req['term'],
					success : function (options) {
						var brolist = [];

						$.each(options, function (title, args) {
							var bro = {};
							bro['value'] = title;
							bro['tag'] = args['tag'] || '';

							brolist.push(bro);
						});

						input.removeClass("input_loading");
						callback(brolist);

						if (brolist.length < 1) {
							showQueryError({
								message : messages.not_found
							});
						}
					},
					error : function (jqXHR) {
						callback([]);

						input.removeClass('input_loading');
						showQueryError({
							status : jqXHR.status
						});
					}
				});
			},

			minLength: 2,
			select : function (event, ui) {
				$('#query_tag').val(ui.item.tag);
			},
		})
		.addClass(input.val() != default_input_val && 'query_normal' || 'query_default')
		.addClass('ui-widget-content ui-widget');

	var form = $('form#query_form');

	$('#submit').button();

	form.submit(function () {
		if (!input.val() || input.val() == default_input_val) {
			$('#query').focus();
			return false;
		}

		directQuery(input.val(), [ $('#query_tag').val() ]);

		return false;
	});

	$('#home')
		.button({
			icons : {
				primary : 'ui-icon-home'
			},
		});
}
