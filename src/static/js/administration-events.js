window.onload = function() {
	init();
}

/**
 * Runs a list of methods on window.onload
 * 
 * @author Maarten van den Hoek
 */
function init() {
	changeInputs();
	addDatePickers();
}


function addDateEntryDatepicker() {
	
}
/**
 * 
 * 
 * @author Maarten van den Hoek
 */
function addDatePickers(o, h) {
	$("#i-datepicker-event-1").datepicker({
		onSelect : function(date, inst) {
			var d = new Date(Date.parse($(this).datepicker('getDate')));
			var df = $.datepicker.formatDate('yy-mm-dd', d);
			$(this).parent().find('.i-date-event').attr('value', df);
		}
	});
	$("#i-reminder-datepicker").datepicker({
		onSelect : function(date, inst) {
			var d = new Date(Date.parse($(this).datepicker('getDate')));
			var df = $.datepicker.formatDate('yy-mm-dd', d);
			$('#i-reminder-date').attr('value', df);
		}
	});
	$.datepicker.setDefaults($.datepicker.regional['nl']);
	$.datepicker.setDefaults({
		dateFormat : 'dd MM yy'
	});
}

/**
 * Add different classes to all different input fields for styling purpose.
 * 
 * @author Maarten van den Hoek
 */
function changeInputs() {
	var $ = jQuery;
	$('input').each(function(i, o) {
		if ($(o).attr('type')) {
			if ($(o).attr('type') == 'text') {
				$(o).addClass('i-t');
			} else if ($(o).attr('type') == 'submit') {
				$(o).addClass('i-s');
			}
		}
	});
}

/**
 * Add a date entry to the date section for a new event
 * 
 * @author Maarten van den Hoek
 * @returns {Boolean}
 */
function addDateEntry() {
	var $ = jQuery;
	var n = $('.date-entry').length;
	var o = clearDateEntry($('.date-entry:first').clone(true));
	$(o).find('.i-nr').attr('value', ++n);
	$(o).find('.date-nr').text(n);
	$('#i-add-date-entry').before(o);
	return false;
}

/**
 * Remove selected date entries from the date section for a new event
 * 
 * @author Maarten van den Hoek
 * @returns {Boolean}
 */
function removeDateEntries() {
	var $ = jQuery;
	var n = $('.date-entry').length;
	var c = 0;
	$('.date-entry').each(function(i, o) {
		if ($(o).find('.i-remove-date:checked').length > 0) {
			if (n > 1) {
				$(o).remove();
				n--;
			} else if (n == 1) {
				o = clearDateEntry(o);
				$(o).find('.i-nr').attr('value', ++c);
				$(o).find('.date-nr').text(c);
			}
		} else {
			$(o).find('.i-nr').attr('value', ++c);
			$(o).find('.date-nr').text(c);
		}
	});
	return false;
}

/**
 * Empty the (visible) inputfiels of a date entry for a new event.
 * 
 * @author Maarten van den Hoek
 * @param o
 *            jQuery object to be processed
 * @returns jQuery object with empty input fields
 */
function clearDateEntry(o) {
	var $ = jQuery;
	$(o).find('.i-datepicker-event').attr('value', "");
	$(o).find('.i-starttime').attr('value', "");
	$(o).find('.i-slots').attr('value', "");
	$(o).find('.i-remove-date').attr('checked', false);
	$(o).find('.i-date-event').attr('value', '');
	return o;
}
