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
	addInitialDatePickers();
}

/**
 * Add the initial datePickers to the date fields when the page is loaded.
 * 
 * @author Maarten van den Hoek
 */
function addInitialDatePickers() {
	addDateEntryDatepicker(1);
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
 * 
 * 
 * @param n the number of the date-entry to put the datepicker on. 
 * @author Maarten van den Hoek
 */
function addDateEntryDatepicker(n) {
	$("#i-datepicker-event-" + n).datepicker({
		onSelect : function(date, inst) {
			var d = new Date(Date.parse($(this).datepicker('getDate')));
			var df = $.datepicker.formatDate('yy-mm-dd', d);
			$('#i-date-event-' + n).attr('value', df);
		}
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
	var o = $('#date-entry-sample').clone(true);
	$(o).find('.date-nr').text(++n);
	
	updateEntryIds(o, 0, n);
	
	$(o).removeAttr('id');
	$(o).addClass('date-entry');
	$('#i-add-date-entry').before(o);
	addDateEntryDatepicker(n);
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
	$('.date-entry').each(
		function(i, o) {
			$('#i-datepicker-event-' + (i+1)).datepicker('destroy'); 
			if ($(o).find('.i-remove-date:checked').length > 0) {
				if (n > 1) {
					$(o).remove();
					n--;
				} else if (n == 1) {
					o = clearDateEntry(o);
					$(o).find('.i-nr').attr('value', ++c);
					$(o).find('.date-nr').text(c);
					updateEntryIds(o, i+1, c);
					addDateEntryDatepicker(c);
				}
			} else {
				$(o).find('.i-nr').attr('value', ++c);
				$(o).find('.date-nr').text(c);
				updateEntryIds(o, i+1, c);
				addDateEntryDatepicker(c);
			}
		});
	return false;
}

/**
 * Empty the (visible) inputfiels of a date entry for a new event.
 * 
 * @author Maarten van den Hoek
 * @param o jQuery object to be processed
 * @returns jQuery object with empty input fields
 */
function clearDateEntry(o) {
	var $ = jQuery;
	$(o).find('.i-date-event').attr('value', '');
	$(o).find('.i-datepicker-event').attr('value', "");
	$(o).find('.i-starttime').attr('value', "");
	$(o).find('.i-slots').attr('value', "");
	$(o).find('.i-remove-date').attr('checked', false);
	return o;
}

/**
 * Change the ids of the input fields so that
 *
 * @author Maarten van den Hoek
 * @param o The jQuery object where to find the input fields that need to be changed.
 * @param i the current number
 * @param n the new number
 */
function updateEntryIds(o, i, n) {
	$(o).find('#i-nr-' + i).attr('value', n);
	$(o).find('#i-nr-' + i).attr('id', 'i-nr-' + n);
	$(o).find('#i-date-event-' + i).attr('id', 'i-date-event-' + n);
	$(o).find('#i-datepicker-event-' + i).attr('id', 'i-datepicker-event-' + n);
	$(o).find('#i-starttime-' + i).attr('id', 'i-starttime-' + n);
	$(o).find('#i-slots-' + i).attr('id', 'i-slots-' + n);
	$(o).find('#i-remove-date-' + i).attr('id', 'i-remove-date-' + n);
}
