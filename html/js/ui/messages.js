
// ok, this is stupid, but js don't have string formatting methods
function format(string, args) {
	var formatted = string;

	for (key in args) {
	    if (args.hasOwnProperty(key)) {
	    	formatted = formatted.replace('%{' + key + '}', args[key]);
	    }
	}

	return formatted;
}

var messages =
{
	not_found :
		'Ничего не найдено',

	query_error :
		'Не получилось обработать ваш запрос, \
		машина ответила числом %{status}. Обычно это означает, что техника устала \
		и ей надо отдохнуть. Но если вам срочно, то \
		<a href="mailto:fyodor@malmash.com">напишите</a> нам и мы постараемся \
		что-нибудь придумать.',

	general_failure :
		'Похоже, что машина в данный момент не работает. \
		Попробуйте зайти позже или \
		<a href="mailto:fyodor@malmash.com">напишите</a> нам об этом и мы \
		обязательно всё починим.',

	broplus_title :
		'Добавить к сравнению',

	packlink_title :
		'Перейти к стае',

	profilelink_title :
		'Перейти к характеристике',
}
