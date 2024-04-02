$(document).ready(function () {
    setTimeout(function () {
        $(".alert").slideUp(500, function () {
            $(this).remove();
        });
    }, 5000);
});