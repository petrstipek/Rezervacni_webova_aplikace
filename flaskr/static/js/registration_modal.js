$(document).ready(function () {
    var submission = false;

    //localStorage.setItem("modalShown", "false");
    //$("#registrationModal").show();

    $('#continueWithReg').change(function () {
        if ($(this).is(':checked')) {
            $('#continueWithoutReg').prop('checked', false);
            $('#passwordField').slideDown();
        } else {
            $('#passwordField').slideUp();
        }
    });

    $('#continueWithoutReg').change(function () {
        if ($(this).is(':checked')) {
            $('#continueWithReg').prop('checked', false);
            $('#passwordField').slideUp();
        }
    });

    $('.close-button').click(function () {
        $('#registrationModal').hide();
    });


    $("#reservation-form").on("submit", function (event) {
        if (submission == false && localStorage.getItem("modalShown") !== "true") {
            event.preventDefault();
            submission = true;
            $("#registrationModal").show();
            localStorage.setItem("modalShown", "true");
        }
    });

    $('#modalSubmitButton').click(function () {
        document.getElementById("reservation-form").submit();
    });

});
