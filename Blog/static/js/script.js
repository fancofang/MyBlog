$(function () {
    function render_time() {
        return moment($(this).data('timestamp')).format('lll')
    }
    $('[data-toggle="tooltip"]').tooltip(
        {title: render_time}
    );

});
$(document).ready(function() {
    window.setTimeout(function() {
    $('.alert').fadeTo(500,0.5).slideUp(500,function(){$('.alert').remove()});
    }, 2000);
});