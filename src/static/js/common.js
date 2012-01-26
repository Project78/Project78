window.onload = function() {
	init();
}

/**
 * Runs a list of methods on window.onload
 * 
 * @author Maarten van den Hoek
 */
function init() {
	addInputClasses();
}

/**
 * Add different classes to all different input fields for styling purpose.
 * 
 * @author Maarten van den Hoek
 */
function addInputClasses() {
	var $ = jQuery;
	$('input').each(function(i, o) {
		if ($(o).attr('type')) {
			if ($(o).attr('type') == 'text' || $(o).attr('type') == 'password') {
				$(o).addClass('i-t');
			} else if ($(o).attr('type') == 'submit') {
				$(o).addClass('i-s');
			}
		}
	});
}