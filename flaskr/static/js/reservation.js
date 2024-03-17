$(document).ready(function () {
    var selectedDate = '';

    $('#reservation_tel_number').on('input', function () {
        var isPhone = /^(\+?\d{1,4}\s?)?(\d{3}\s?){3}$|^\d{9}$/.test($(this).val());
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

    $('#name').on('input', function () {
        var isValidName = /^[a-zA-ZáéíóúýčďěňřšťžůÁÉÍÓÚÝČĎĚŇŘŠŤŽŮ\s]+$/.test($(this).val());
        if (isValidName) {
            $(this).css('border', '2px solid green');
            $('#name_error').css('visibility', 'hidden');
            setTimeout(() => {
                $(this).animate({ borderColor: '#cccccc' }, 'slow');
            }, 2000);
        } else {
            $(this).css('border', '2px solid red');
            $('#name_error').css('visibility', 'visible').text('name error');
        }
    });

    $('#surname').on('input', function () {
        var isValidSurname = /^[a-zA-ZáéíóúýčďěňřšťžůÁÉÍÓÚÝČĎĚŇŘŠŤŽŮ\s]+$/.test($(this).val());
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

    $('#age_client_main').on('input', function () {
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

    function fetchAvailableTimes() {
        var instructorId = $('#lesson_instructor').val();
        var lessonType = $('#lesson_type').val();

        if (lessonType === 'individual' && instructorId) {
            $.ajax({
                ///reservations-api/lessons/instructorid/available-times
                url: '/reservations-api/get-available-times/individual/' + instructorId,
                type: 'GET',
                success: function (data) {
                    updateAvailableTimes(data);
                    selectedDate = $('#datepicker').val();
                    $("input[name='date']").val(selectedDate);
                },
                error: function (error) {
                    console.error('Error fetching available times:', error);
                }
            });
        } else if (lessonType === 'group') {
            $.ajax({
                //reservations-api/lessons/available-times
                url: '/reservations-api/get-available-times/group',
                type: 'GET',
                success: function (data) {
                    console.log("group function ")
                    updateAvailableTimes(data);
                    //selectedDate = $('#datepicker').val();
                    //$("input[name='date']").val(selectedDate);
                    console.log(selectedDate)
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
            $('#client_student_details_section').show();
        } else {
            $('#client_student_details_section').hide();
        }
    }).change();

    $('#more_students_checkbox').change(function () {
        if (this.checked) {
            $('#student_details_section').show();
        } else {
            $('#student_details_section').hide();
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

    //flask wont submit disabled fields
    $('form').submit(function () {
        $('#lesson_length').prop('disabled', false);
        $('#lesson_instructor').prop('disabled', false);
    });

    $('#name').keypress(restrictInputToText);
    $('#surname').keypress(restrictInputToText);
    $('#reservation_tel_number').keypress(restrictInputToNumbers);

    function restrictInputToText(event) {
        var regex = /^[a-zA-ZáéíóúýčďěňřšťžůÁÉÍÓÚÝČĎĚŇŘŠŤŽŮ\s]*$/;
        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        if (!regex.test(key)) {
            event.preventDefault();
            return false;
        }
    }

    function restrictInputToNumbers(event) {
        var regex = /^[0-9]*$/;
        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        if (!regex.test(key)) {
            event.preventDefault();
            return false;
        }
    }

    var isFormValid = false;

    $('.btn-send-reservation').click(function (event) {
        event.preventDefault();

        isFormValid = true;
        var fields = ['#name', '#surname', '#email', '#reservation_tel_number, #age_client_main'];

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
            alert("Prosím, vyplňte všechna povinná pole.");
        }
    });

    window.onSubmit = function (token) {
        if (isFormValid) {
            $('#reservation-form').submit();
        } else {
            console.log('Chyba validace!');
        }
    };
});