$(document).ready(function () {
    var selectedDate = '';

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

    function fetchAvailableTimes() {
        var instructorId = $('#lesson_instructor').val();
        var lessonType = $('#lesson_type').val();

        if (lessonType === 'individual' && instructorId) {
            $.ajax({
                url: '/reservations-api/lessons/' + instructorId + '/available-times',
                type: 'GET',
                success: function (data) {
                    updateAvailableTimes(data);
                    console.log(data)
                    selectedDate = $('#datepicker').val();
                    $("input[name='date']").val(selectedDate);
                },
                error: function (error) {
                    console.error('Error fetching available times:', error);
                }
            });
        } else if (lessonType === 'group') {
            $.ajax({
                url: '/reservations-api/lessons/available-times',
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

    $('#lesson_instructor').change(fetchAvailableTimes);

    $('#lesson_type').change(fetchAvailableTimes);

    function toggleRequired(clientNumber) {
        const fields = [
            $(`#surname_client${clientNumber}`),
            $(`#age_client${clientNumber}`),
            $(`#experience_client${clientNumber}`)
        ];

        const isNameFilled = $(`#name_client${clientNumber}`).val().trim() !== '';

        fields.forEach($field => {
            if (isNameFilled) {
                $field.attr('required', 'required');
            } else {
                $field.removeAttr('required');
            }
        });
    }

    [1, 2, 3].forEach(clientNumber => {
        $(`#name_client${clientNumber}`).on('input', function () {
            toggleRequired(clientNumber);
        });
    });

    $('#student_client_checkbox').change(function () {
        if (this.checked) {
            $('#client_student_details_section').slideDown();
        } else {
            $('#client_student_details_section').slideUp();
        }
    }).change();

    $('#more_students_checkbox').change(function () {
        if (this.checked) {
            $('#student_details_section').slideDown();
        } else {
            $('#student_details_section').slideUp();
        }
    });

    var availableTimesInd = ($('#datepicker').data('available-times-ind'));
    var availableTimesGroup = ($('#datepicker').data('available-times-group'));

    function updateAvailableTimes(data_times) {
        if (!selectedDate || typeof data_times === 'undefined') {
            return;
        }

        selectedDate = selectedDate.trim();

        if (!data_times.hasOwnProperty(selectedDate)) {
            $('.times-container').html('<div class="no-times-available">Pro vybrané parametry není dostupná žádná hodina!</div>');
            return;
        }

        var timesForSelectedDate = data_times[selectedDate];

        if (!Array.isArray(timesForSelectedDate)) {
            console.log("Times for selected date is not an array:", timesForSelectedDate);
            $('.times-container').html("Chyba při zobrazování dostupných hodin!");
            return;
        }
        var timesHtml = '<div class="times-grid">';

        timesForSelectedDate.sort(function (a, b) {
            return new Date('1970/01/01 ' + a[0]) - new Date('1970/01/01 ' + b[0]);
        });

        timesForSelectedDate.forEach(function (timeCountPair, index) {
            if (index % 3 === 0) {
                if (index !== 0) {
                    timesHtml += '</div>';
                }
                timesHtml += '<div class="times-grid-row">';
            }

            var time = timeCountPair[0];
            var count = timeCountPair[1];
            timesHtml += `<div class="time-slot">
                            <label class="time-slot-label d-flex justify-content-between align-items-center">
                                <span class="time">${time}</span>
                                <span class="count">Volné hodiny k rezervaci: ${count}</span>
                                <input class="form-check-input" type="radio" name="time" value="${time}" />
                            </label>
                        </div>`;

            if (index === timesForSelectedDate.length - 1) {
                timesHtml += '</div>';
            }
        });

        timesHtml += '</div>';
        document.querySelector('.times-container').innerHTML = timesHtml;
    }

    $.datepicker.regional['cs'] = {
        closeText: 'Zavřít',
        prevText: '&#x3C;Dříve',
        nextText: 'Později&#x3E;',
        currentText: 'Nyní',
        monthNames: ['Leden', 'Únor', 'Březen', 'Duben', 'Květen', 'Červen',
            'Červenec', 'Srpen', 'Září', 'Říjen', 'Listopad', 'Prosinec'],
        monthNamesShort: ['Led', 'Úno', 'Bře', 'Dub', 'Kvě', 'Čvn',
            'Čvc', 'Srp', 'Zář', 'Říj', 'Lis', 'Pro'],
        dayNames: ['Neděle', 'Pondělí', 'Úterý', 'Středa', 'Čtvrtek', 'Pátek', 'Sobota'],
        dayNamesShort: ['Ne', 'Po', 'Út', 'St', 'Čt', 'Pá', 'So'],
        dayNamesMin: ['Ne', 'Po', 'Út', 'St', 'Čt', 'Pá', 'So'],
        weekHeader: 'Tyd',
        dateFormat: 'dd.mm.yy',
        firstDay: 1,
        isRTL: false,
        showMonthAfterYear: false,
        yearSuffix: ''
    };

    $.datepicker.setDefaults($.datepicker.regional['cs']);

    $('#datepicker').datepicker({
        dateFormat: 'yy-mm-dd',
        minDate: 0,
        firstDay: 1,
        onSelect: function (dateText) {
            selectedDate = dateText;
            $("input[name='date']").val(dateText);
            updateAvailableTimes(fetchAvailableTimes());
        }
    }).datepicker("setDate", new Date());

    selectedDate = $('#datepicker').val();
    $("input[name='date']").val(selectedDate);
    updateAvailableTimes(fetchAvailableTimes());

    $('.times-container').on('click', '.time-slot', function () {
        console.log("Time slot clicked");
        $('.times-container .time-slot').removeClass('selected');
        $(this).addClass('selected');
        var radioButton = $(this).find('input[type="radio"]');
        console.log("New time selected:", radioButton.val());
        radioButton.prop('checked', true);
        radioButton.change();
        $("input[name='time_reservation']").val(radioButton.val());
    });


    $(document).ready(function () {
        $('#lesson_type').change(function () {
            const lessonType = $(this).val();

            if (lessonType === 'group') {
                $('#lesson_length').val('1hodina');
                $('#lesson_instructor_choices').val('0');
                $('#lesson_instructor').val('0');
                $('#lesson_length').prop('disabled', true);
                $('#lesson_instructor').prop('disabled', true);
            } else {
                $('#lesson_length').prop('disabled', false);
                $('#lesson_instructor').prop('disabled', false);
            }
        });
    });

    function copyAndValidate(sourceSelector, targetSelector) {
        var value = $(sourceSelector).val();
        $(targetSelector).val(value);
    }

    $('#name').on('input', function () {
        copyAndValidate('#name', '#name_client_hidden');
    });
    $('#surname').on('input', function () {
        copyAndValidate('#surname', '#surname_client_hidden');
    });

    copyAndValidate('#name', '#name_client_hidden',);
    copyAndValidate('#surname', '#surname_client_hidden');

    //flask wont submit disabled fields
    $('form').submit(function () {
        $('#lesson_length').prop('disabled', false);
        $('#lesson_instructor').prop('disabled', false);
    });

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

    var isFormValid = false;
    var student_client = $("#student_client_checkbox").prop('checked');
    console.log(student_client)

    $('.btn-send-reservation').click(function (event) {
        event.preventDefault();
        var student_client = $("#student_client_checkbox").prop("checked");
        var more_students = $("#more_students_checkbox").prop("checked");

        if (!student_client && !more_students) {
            var fields = ['#name', '#surname', '#email', '#reservation_tel_number'];
        }
        if (student_client) {
            var fields = ['#name', '#surname', '#email', '#reservation_tel_number', '#age_client_main'];
        }
        if (more_students) {
            var fields = ['#name', '#surname', '#email', '#reservation_tel_number', '#name2', '#name3', '#surname2', '#surname3', '#age2', '#age3'];
        }
        isFormValid = true;

        fields.forEach(function (selector) {
            var input = $(selector);
            if (!input.val().trim()) {
                isFormValid = false;
                input.css('border', '2px solid red');
            } else {
                input.css('border', '');
            }
        });

        if (!isFormValid) {
            if (!student_client && !more_students) {
                alert("Prosím, zvolte žáky lekce a doplňte příslušná pole!")
            } else {
                alert("Prosím, vyplňte všechna povinná pole!");
            }
        }
    });

    window.onSubmit = function (token) {
        if (isFormValid) {
            $('#reservation-form').submit();
        } else {
            console.log('Chyba validace!');
        }
    };

    function adjustColumnHeights() {
        var leftColumnHeight = $('.left-column').outerHeight();
        $('.right-column').css('min-height', leftColumnHeight);
    }

    $("#datepicker").datepicker({
        onSelect: function (dateText, inst) {
            adjustColumnHeights();
        },
        onChangeMonthYear: function (year, month, inst) {
            adjustColumnHeights();
        }
    });

    $(document).on('click', '.ui-datepicker-next, .ui-datepicker-prev', function () {
        adjustColumnHeights();
    });

    adjustColumnHeights();


});