$(document).ready(function () {

    $('#reservation_tel_number').on('input', function () {
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
    validateNameFields("#name2");
    validateNameFields("#name3");

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

    validateSurnameFields("#surname");
    validateSurnameFields("#surname2");
    validateSurnameFields("#surname3");

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

    function validateAgeFields(fieldSelector) {
        $(fieldSelector).on('input', function () {
            if ($(this).val().trim() !== '') {
                $(this).css('border', '2px solid green');
                $('#age_error').css('visibility', 'hidden');
                setTimeout(() => {
                    $(this).css('border-color', '#cccccc');
                }, 2000);
            } else {
                $(this).css('border', '2px solid red');
                $('#age_error').css('visibility', 'visible').text('age error');
            }
        });
    }

    validateAgeFields("#age_client_main");
    validateAgeFields("#age2");
    validateAgeFields("#age3");

    $('#name').keypress(restrictInputToText);
    $('#surname').keypress(restrictInputToText);
    $('#reservation_tel_number').keypress(restrictInputToNumbers);

    $('#name2').keypress(restrictInputToText);
    $('#surname2').keypress(restrictInputToText);
    $('#name3').keypress(restrictInputToText);
    $('#surname4').keypress(restrictInputToText);

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


    var selectedDate = $('#datepicker').val();
    $('#datepicker').on('change', fetchAvailableTimes);
    function fetchAvailableTimes() {
        var instructorId = $('#lesson_instructor').val();
        var lessonType = $('#lesson_type').val();
        var selectedDate = $('#datepicker').val();

        var url = lessonType === 'individual' ? `/reservations-api/lessons/${instructorId}/available-times` : '/reservations-api/lessons/available-times';

        if (selectedDate) {
            $.ajax({
                url: "/reservations-api/lessons/0/available-times",
                data: {
                    reservation_date: selectedDate
                },
                type: 'GET',
                success: function (data) {
                    updateAvailableTimes(data);
                },
                error: function (error) {
                    console.error('Error fetching available times:', error);
                }
            });
        }
    }

    function updateAvailableTimes(data) {
        var $timeSelect = $('#reservation_time');
        var selectedDate = $('#datepicker').val();

        $timeSelect.empty();

        if (data[selectedDate]) {
            data[selectedDate].forEach(function (timeSlot) {
                $timeSelect.append($('<option>', {
                    value: timeSlot[0],
                    text: timeSlot[0]
                }));
            });
        } else {
            $timeSelect.append($('<option>', {
                value: '',
                text: 'No available times'
            }));
        }
    }

    $('#reservation-change-form').submit(function () {
        var $timeSelect = $('#reservation_time');
        if (!$timeSelect.val()) {
            $timeSelect.val($('#initialTime').val());
        }
    });

    $('#reservation-change-form').submit(function (event) {
        var isStudentChecked = $('#student_client').is(':checked');
        var isMoreStudentsChecked = $('#more_students').is(':checked');

        if (!isStudentChecked && !isMoreStudentsChecked) {
            alert('Musí zakšrtnout alespoň jednu možnost žáků!');
            event.preventDefault();
        }
    });

    var studentCount = $('#reservation-change-form').data('student-count');
    console.log(studentCount);

    var studentClient = $('#reservation-change-form').data('student-client');
    console.log(studentClient, "studentClient");

    function checkboxes() {
        if (studentClient == true) {
            $('#student_client').prop('checked', true);
        }
        if (studentCount >= 2) {
            $('#more_students').prop('checked', true);
        }

        /*
        if ($('#age_client1').val() === '' && $('#age_client2').val() === '') {
            $('#more_students').prop('checked', false);
        }

        if ($('#age_client').val() !== '') {
            $('#student_client').prop('checked', true);
        }
        */
    };

    function updateVisibility() {
        var showStudentClient = $('#student_client').is(':checked');
        var showMoreStudents = $('#more_students').is(':checked');

        if (showStudentClient && showMoreStudents) {
            $("#zak1-section, #zak2-section, #zak3-section").slideDown();
            copyAndValidate('#name', '#name_client_hidden',);
            copyAndValidate('#surname', '#surname_client_hidden');
        } else if (showStudentClient) {
            $("#zak1-section").slideDown();
            $("#zak2-section, #zak3-section").slideUp();
            copyAndValidate('#name', '#name_client_hidden',);
            copyAndValidate('#surname', '#surname_client_hidden');
        } else if (showMoreStudents) {
            $("#zak2-section, #zak3-section").slideDown();
            $("#zak1-section").slideUp();
            copyAndValidate('#name', '#name_client_hidden',);
            copyAndValidate('#surname', '#surname_client_hidden');
        } else {
            $("#zak1-section, #zak2-section, #zak3-section").slideUp();
            copyAndValidate('#name', '#name_client_hidden',);
            copyAndValidate('#surname', '#surname_client_hidden');
        }
    }

    function updateHiddenFields() {
        var isChecked = $('#student_client').is(':checked');

        if (isChecked) {
            $('#name_client_hidden').val($('#name_client1').val());
            $('#surname_client_hidden').val($('#surname_client1').val());
        } else {
            $('#name_client_hidden').val('');
            $('#surname_client_hidden').val('');
        }
    }

    $('#student_client').change(updateHiddenFields);

    checkboxes();
    updateVisibility();
    updateHiddenFields();
    fetchAvailableTimes();
    updateAvailableTimes(selectedDate);

    $('#student_client, #more_students').change(updateVisibility);

    function copyAndValidate(sourceSelector, targetSelector) {

        var value = $(sourceSelector).val();
        $(targetSelector).val(value);
    };

    copyAndValidate('#name', '#name_client_hidden',);
    copyAndValidate('#surname', '#surname_client_hidden');

    $('#name').on('input', function () {
        copyAndValidate('#name', '#name_client_hidden');
    });
    $('#surname').on('input', function () {
        copyAndValidate('#surname', '#surname_client_hidden');
    });
});

$(document).ready(function () {
    $('#change_time_checkbox').change(function () {
        if ($(this).is(':checked')) {
            $('#date-time-fields').slideDown();
        } else {
            $('#date-time-fields').slideUp();
        }
    });

    $(document).on('click', '.close', function () {
        $('#detailModal').css('display', 'none');
        $('body').removeClass('body-no-scroll');
    });
});