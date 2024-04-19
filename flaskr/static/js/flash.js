$(document).ready(function () {
    setTimeout(function () {
        $(".alert").not('.persistent').slideUp(500, function () {
            $(this).remove();
        });
    }, 5000);

});