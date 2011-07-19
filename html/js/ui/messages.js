
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

var not_found = 'Ничего не найдено';
var query_error = 'Не получилось обработать ваш запрос, \
	машина ответила числом %{status}. Обычно это означает, что техника устала \
	и ей надо отдохнуть. Но если вам срочно, то \
	<a href="mailto:fyodor@malmash.com">напишите</a> нам и мы постараемся \
	что-нибудь придумать.';
var general_failure = 'Похоже, что машина в данный момент не работает. \
	Попробуйте зайти позже или \
	<a href="mailto:fyodor@malmash.com">напишите</a> нам об этом и мы \
	обязательно всё починим.';
var page_error = query_error;
var broplus_title = 'Добавить к сравнению';
var packlink_title = 'Перейти к стае';
var profilelink_title = 'Перейти к характеристике';
