/**
 * FileName: registration.js
 * Description: Script for the registration form validation.
 * Author: Petr Štípek
 * Date Created: 2024
 */

$(document).ready(function () {
    function validateNameFields(fieldSelector) {
        $(fieldSelector).on('input', function () {
            var isValidName = /^[a-zA-ZáéíóúýčďěňřšťžůÁÉÍÓÚÝČĎĚŇŘŠŤŽŮ\s'.-]+$/.test($(this).val());
            if (isValidName) {
                $(this).css('border', '2px solid green');
                $('#name_error').css('visibility', 'hidden');
                setTimeout(() => {
                    $(this).animate({ borderColor: '#cccccc' }, 'slow');
                }, 2000);
            }
            else {
                $(this).css('border', '2px solid red');
                $('#name_error').css('visibility', 'visible').text('name error');
            }
        })
    }

    validateNameFields("#name");

    function validateSurnameFields(fieldSelector) {
        $(fieldSelector).on('input', function () {
            var isValidSurname = /^[a-zA-ZáéíóúýčďěňřšťžůÁÉÍÓÚÝČĎĚŇŘŠŤŽŮ\s'.-]+$/.test($(this).val());
            if (isValidSurname) {
                $(this).css('border', '2px solid green');
                $('#surname_error').css('visibility', 'hidden');
                setTimeout(() => {
                    $(this).animate({ borderColor: '#cccccc' }, 'slow');
                }, 2000);
            } else {
                $(this).css('border', '2px solid red');
                $('#surname_error').css('visibility', 'visible').text('surname error');
            }
        });
    }

    validateSurnameFields("#surname")

    $('#email').on('input', function () {
        var isValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test($(this).val());
        if (isValidEmail) {
            $(this).css('border', '2px solid green');
            $('#email_error').css('visibility', 'hidden');
            setTimeout(() => {
                $(this).animate({ borderColor: '#cccccc' }, 'slow');
            }, 2000);
        } else {
            $(this).css('border', '2px solid red');
            $('#email_error').css('visibility', 'visible').text('email error');
        }
    });

    $('#tel_number').on('input', function () {
        var isPhone = /^(\+?\d{1,3}\s?)?(\d{3}\s?){2,3}\d{3}$/.test($(this).val());
        if (isPhone) {
            $(this).css('border', '2px solid green');
            $('#tel_error').css('visibility', 'hidden');
            setTimeout(() => {
                $(this).animate({ borderColor: '#cccccc' }, 'slow');
            }, 2000);
        } else {
            $(this).css('border', '2px solid red');
            $('#tel_error').css('visibility', 'visible').text('phone error');
        }
    });

    function restrictInputToText(event) {
        var regex = /^[a-zA-ZáéíóúýčďěňřšťžůÁÉÍÓÚÝČĎĚŇŘŠŤŽŮ\s]*$/;
        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        if (!regex.test(key)) {
            event.preventDefault();
            return false;
        }
    }

    $('#name').keypress(restrictInputToText);
    $('#surname').keypress(restrictInputToText);

    function restrictInputToNumbers(event) {
        var regex = /^[0-9+ ]*$/;
        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        if (!regex.test(key)) {
            event.preventDefault();
            return false;
        }
    }

    $('#tel_number').keypress(restrictInputToNumbers);

    function restrictEmail(event) {
        var regex = /[a-zA-Z0-9@.\-_+]/;
        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);

        if (!regex.test(key)) {
            event.preventDefault();
        }
    }

    $('#email').keypress(restrictEmail);
})