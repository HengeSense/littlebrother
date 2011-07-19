
var default_input_val = '';
var current_ident = undefined;

function directQuery(ident) {
	$.bro.idents({
		pattern : ident, 
		success : function (bros) {
			switch (dictSize(bros)) {
			case 0:
				showQueryError({
					message : not_found
				});
				break;
				
			case 1:
				for (key in bros) {
			        if (bros.hasOwnProperty(key)) {
			        	window.location = ('/profile.html?bros=' 
			        		+ prepareNameForUrl(key));
			        	break;
			        }
				}
				break;
			
			default:
				window.location = ('/search.html?search=' + ident);
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
		.val(current_ident || default_input_val)
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
		.autocomplete({ source : function(req, callback) {
			input.addClass('input_loading');
			
			$.bro.idents({ 
				pattern : req['term'], 
				success : function (options) {
					var brolist = [];
					
					$.each(options, function (title, args) {
						brolist.push(title);
					});
					
					input.removeClass("input_loading");
					
					if (brolist.length < 1) {
						showQueryError({
							message : not_found
						});
						return;
					}
					
					callback(brolist);
				},
				error : function (jqXHR) {
					input.removeClass('input_loading');
					showQueryError({
						status : jqXHR.status
					});
				}
			});
		}})
		.addClass(current_ident && 'query_normal' || 'query_default')
		.addClass('ui-widget-content ui-widget');

	var form = $('form#query_form');
	
	$('#submit').button();
	
	form.submit(function () {
		if (!input.val() || input.val() == default_input_val) {
			$('#query').focus();
			return false;
		}
		
		directQuery(input.val());
		
		return false;
	});
	
	$('#home')
		.button({
			icons : {
				primary : 'ui-icon-home'
			}, 
		});
}
