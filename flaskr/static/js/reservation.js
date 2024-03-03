$(document).ready(function () {

    const lessonTypeSelect = document.getElementById('lesson_type');
    const additionalField1Container = document.getElementById('div_lesson_length');
    const additionalField2Container = document.getElementById('div_lesson_instructor');
    const additionalField3Container = document.getElementById('div_lesson_language')

    lessonTypeSelect.addEventListener('change', function () {
        if (this.value === 'individual') {
            additionalField1Container.style.display = '';
            additionalField2Container.style.display = '';
            additionalField3Container.style.display = '';
        } else if (this.value === 'group') {
            additionalField1Container.style.display = 'none';
            additionalField2Container.style.display = 'none';
            additionalField3Container.style.display = 'none';
        }
    });


    function fetchAvailableTimes() {
        var instructorId = $('#lesson_instructor').val();
        var lessonType = $('#lesson_type').val();
        var lessonLength = $('#lesson_length').val();


        if (lessonType === 'individual' && instructorId) {
            $.ajax({
                url: '/reservations-api/get-available-times/individual/' + instructorId,
                type: 'GET',
                success: function (data) {
                    updateAvailableTimes(data);
                    //return data;
                },
                error: function (error) {
                    console.error('Error fetching available times:', error);
                }
            });
        } else if (lessonType === 'group') {
            $.ajax({
                url: '/reservations-api/get-available-times/group',
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
    var selectedDate = '';

    function updateAvailableTimes(data_times) {
        if (!selectedDate || typeof data_times === 'undefined') {
            return;
        }

        selectedDate = selectedDate.trim();

        if (!data_times.hasOwnProperty(selectedDate)) {
            $('.times-container').html("Pro vybrané parametry není dostupná žádná hodina.");
            return;
        }

        var timesForSelectedDate = data_times[selectedDate];

        if (!Array.isArray(timesForSelectedDate)) {
            console.log("Times for selected date is not an array:", timesForSelectedDate);
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

    $('#datepicker').datepicker({
        dateFormat: 'yy-mm-dd',
        onSelect: function (dateText) {
            selectedDate = dateText;
            $("input[name='date']").val(dateText);
            updateAvailableTimes(fetchAvailableTimes());
        }
    }).datepicker("setDate", new Date());

    selectedDate = $('#datepicker').val();
    updateAvailableTimes(fetchAvailableTimes());

    $('.times-container').on('click', '.time-slot', function () {
        $('.times-container .time-slot').removeClass('selected');
        $(this).addClass('selected');
        var radioButton = $(this).find('input[type="radio"]');
        radioButton.prop('checked', true);
        radioButton.change();
    });

    $('.times-container').on('change', 'input[name="time"]', function () {
        if (this.checked) {
            $("input[name='time']").val($(this).val());
        }
    });

    $(document).ready(function () {
        $('#lesson_type').change(function () {
            const lessonType = $(this).val();

            if (lessonType === 'group') {
                $('#lesson_length').prop('disabled', true);
                $('#lesson_instructor').prop('disabled', true);
            } else {
                $('#lesson_length').prop('disabled', false);
                $('#lesson_instructor').prop('disabled', false);
                $('#lesson_language').prop('disabled', false);
            }
        });
    });

});