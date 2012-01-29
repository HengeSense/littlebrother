(function ( $ ) {
	var api_host = "";
	var bro_version = "&version=proto";

	function capitalize(str) {
		words = str.split(' ');
		capitalized = $.map(words, function(value, index) {
			return (value && value[0].toUpperCase()
				+ value.substr(1, value.length - 1).toLowerCase() || '');
		});
		return capitalized.join(' ');
	}

	function apiString(bro) {
		var title = bro.title || '';
		var tag = bro.tag || '';

		return title.toUpperCase().replace('Ё', 'Е') + (tag && ':' + tag || '');
	}

	function idents(args) {
		if (args == undefined) {
			args = {};
		}

		var url = api_host
			+ '/api/?frontend=json&interface=idents&pattern='
			+ apiString({ title : (args.pattern || '') });

		if (args.tags) {
			for (var i = 0; i < args.tags.length; ++i) {
				url += '&tags=' + args.tags[i];
			}
		}

		if (args.limit) {
			url += '&limit=' + args.limit;
		}

		url += '&offset=' + (args.offset || 0) + bro_version;

		$.ajax({
			url : url,
			error : args.error,
			success : function(idents) {
				var options = {};

				$.each(idents, function(index, val) {
					var bro = {};

					bro['title'] = capitalize(val['title']);
					bro['tag'] = val['tag'];
					bro['score'] = val['score'];

					options[bro['title']] = bro;
				});

				if (args.success) {
					args.success(options);
				}
			}
		});
	}
	/*
	function fuzzyIdents(args) {
		if (args == undefined) {
			args = {}
		}

		var url = api_host
			+ '/api/?frontend=json&interface=fuzzyidents&pattern='
			+ apiString(args.pattern || '')
			+ '&offset=0'
			+ bro_version;

		$.ajax({
			url : url,
			error : args.error,
			success : function(idents) {
				var options = {};

				$.each(idents, function(index, val) {
					var bro = {};

					bro['tag'] = val['tag'];
					bro['score'] = val['score'];

					options[capitalize(val['title'])] = bro;
				});

				if (args.success) {
					args.success(options);
				}
			}
		});
	}
	*/
	function urls(args) {
		if (args == undefined) {
			args = {}
		}

		var url = api_host
			+ '/api/?frontend=json&interface=urls';

		$.each(args.bros || [], function (index, bro) {
			url += '&idents=' + apiString(bro);
		});

		if (args.titles_pattern) {
			url += '&title=' + args.titles_pattern;
		}

		if (args.domain_pattern) {
			url += '&domain=' + args.domain_pattern;
		}

		if (args.limit) {
			url += '&limit=' + args.limit;
		}

		url += '&offset=' + (args.offset || 0) + bro_version;

		$.ajax({
			url : url,
			error : args.error,
			success : function(urls) {
				var refs = {};

				$.each(urls, function(index, val) {
					refs[val['ref']] = val['ref_title'];
				});

				if (args.success) {
					args.success(refs);
				}
			}
		});
	}

	function connections(args) {
		if (args == undefined) {
			args = {}
		}

		var url = api_host
			+ '/api/?frontend=json&interface=connections';

		$.each(args.bros || [], function (index, bro) {
			url += '&idents=' + apiString(bro);
		});

		if (args.pattern) {
			url += '&pattern=' + apiString({ title : args.pattern });
		}

		if (args.tags) {
			for (var i = 0; i < args.tags.length; ++i) {
				url += '&tags=' + args.tags[i];
			}
		}

		if (args.limit) {
			url += '&limit=' + args.limit;
		}

		url += '&offset=' + (args.offset || 0) + bro_version;

		$.ajax({
			url : url,
			error : args.error,
			success : function(connections) {
				var options = {};

				$.each(connections, function(index, val) {
					var bro = {};

					bro['title'] = capitalize(val['title']);
					bro['tag'] = val['tag'];
					bro['median'] = val['median'];
					bro['average'] = val['average'];
					bro['score'] = val['score'];

					options[bro['title'] + ':' + bro['tag']] = bro;
				});

				if (args.success) {
					args.success(options)
				}
			}
		});
	}

	function pack(args) {
		if (args == undefined) {
			args = {}
		}

		var url = api_host
			+ '/api/?frontend=json&interface=pack&idents='
			+ apiString(args.bro || '');

		if (args.tags) {
			for (var i = 0; i < args.tags.length; ++i) {
				url += '&tags=' + args.tags[i];
			}
		}

		if (args.pattern) {
			url += '&pattern=' + args.pattern;
		}

		url += '&offset=' + (args.offset || 0) + bro_version;

		$.ajax({
			url : url,
			error : args.error,
			success : function(pack) {
				var options = {};

				$.each(pack, function(index, val) {
					var bro = {};

					bro['title'] = capitalize(val['title']);
					bro['tag'] = val['tag'];
					bro['score'] = val['score'];
					bro['level'] = val['level'];

					options[bro['title']] = bro;
				});

				if (args.success) {
					args.success(options);
				}
			}
		});
	}

	function stats(args) {
		if (args == undefined) {
			args = {}
		}

		var url = api_host
			+ '/api/?frontend=json&interface=stats'
			+ bro_version;

		function fix(records, keys) {
			if (!records) {
				return records;
			}

			$.each(keys, function (index, key) {
				if (records[key])
					records[key] = capitalize(records[key]);
			});

			return records;
		}

		$.ajax({
			url : url,
			error : args.error,
			success : function(stats) {
				var records = fix(stats[0],
					['top_ident', 'bottom_ident', 'top_name', 'bottom_name', 'top_org', 'bottom_org']);

				if (args.success) {
					args.success(records || {});
				}
			}
		});
	}

	$.bro = {
		stats : stats,
		idents : idents,
//		fuzzyIdents : fuzzyIdents,
		connections : connections,
		urls : urls,
		pack : pack,
	};

})(jQuery);

