$('.submitButton').on('click', function() {
    var $this = $(this);
    $this.find('.spinner-border').show();
    $this.prop('disabled', true);
});