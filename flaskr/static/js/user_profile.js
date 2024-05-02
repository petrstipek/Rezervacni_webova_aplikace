/**
 * FileName: user_profile.js
 * Description: Script for the user profile page. Page for updating user information.
 * Author: Petr Štípek
 * Date Created: 2024
 */

$(document).ready(function () {
    function restrictInputToText(event) {
        var regex = /^[a-zA-ZáéíóúýčďěňřšťžůÁÉÍÓÚÝČĎĚŇŘŠŤŽŮ\s]*$/;
        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        if (!regex.test(key)) {
            event.preventDefault();
            return false;
        }
    }

    function restrictInputToNumbers(event) {
        var regex = /^[0-9+ ]*$/;
        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        if (!regex.test(key)) {
            event.preventDefault();
            return false;
        }
    }

    function restrictEmail(event) {
        var regex = /[a-zA-Z0-9@.\-_+]/;
        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);

        if (!regex.test(key)) {
            event.preventDefault();
        }
    }

    $('#name').keypress(restrictInputToText);
    $('#surname').keypress(restrictInputToText);
    $('#email').keypress(restrictEmail);
    $('#tel_number').keypress(restrictInputToNumbers);

})