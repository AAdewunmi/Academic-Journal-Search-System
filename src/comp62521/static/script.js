$(document).ready(function() {
	setTableColumnWidths();
});
function setTableColumnWidths() {
	// Heavily modified version of the code from 
	// http://stackoverflow.com/questions/17067294/html-table-with-100-width-with-vertical-scroll-inside-tbody

	// Change the selector if needed
	var $table = $('table'),
	    $bodyCells = $table.find('tbody tr:first').children(),
	    $headCells = $table.find('thead tr:first').children(),
	    colBodyWidth,
	    colHeadWidth


	// Get the tbody columns width array
	colBodyWidth = $bodyCells.map(function() {
	    return $(this).width();
	}).get();

	// Get the tbody columns width array
	colHeadWidth = $headCells.map(function() {
	    return $(this).width();
	}).get();

	// Set the width of thead columns
	$table.find('thead tr').children().each(function(i, v) {
	    $(v).css('min-width', Math.max(colBodyWidth[i], colHeadWidth[i]));
	});

	// Set the width of tbody columns
	$table.find('tbody tr').first().children().each(function(i, v) {
	    $(v).css('min-width', Math.max(colBodyWidth[i], colHeadWidth[i]));
	}); 
}