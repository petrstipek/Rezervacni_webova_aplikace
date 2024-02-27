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
                url: '/get-available-times/individual/' + instructorId,
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
                url: '/get-available-times/group',
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
            $('.times-container').html("No available times for selected date.");
            return;
        }

        var timesForSelectedDate = data_times[selectedDate];

        if (!Array.isArray(timesForSelectedDate)) {
            console.log("Times for selected date is not an array:", timesForSelectedDate);
            return;
        }

        var timesHtml = timesForSelectedDate.map(function (timeCountPair) {
            var time = timeCountPair[0];
            var count = timeCountPair[1];

            return `<label><input class="form-check-input" type="radio" name="time" value="${time}" /> ${time} - Available Slots: ${count}</label><br>`;
        }).join('');

        $('.times-container').html(timesHtml);
    }

    $('#datepicker').datepicker({
        dateFormat: 'yy-mm-dd',
        onSelect: function (dateText) {
            selectedDate = dateText;
            $("input[name='date']").val(dateText);
            updateAvailableTimes(fetchAvailableTimes());
        }
    });

    $('.times-container').on('change', 'input[name="time"]', function () {
        if (this.checked) {
            $("input[name='time']").val($(this).val());
        }
    });
});