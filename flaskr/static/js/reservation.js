$(document).ready(function () {

    $('#lesson_instructor').change(function () {
        var instructorId = $(this).val();
        $.ajax({
            url: '/get-available-times/' + instructorId,
            type: 'GET',
            success: function (data) {
                // Assuming 'data' is a list of strings representing available times
                // Update your date picker with these times
                updateDatePicker(data);
            },
            error: function (error) {
                console.log(error);
            }
        });
    });

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
    })

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

    function updateAvailableTimes() {
        if (!selectedDate) {
            return;
        }

        var lessonType = $('#lesson_type').val();

        var times = lessonType === 'individual' ? availableTimesInd[selectedDate] : availableTimesGroup[selectedDate];
        console.log(times)
        times = times || [];

        var timesHtml = times.map(function (time) {
            return `<label><input type="checkbox" name="time" value="${time}" /> ${time}</label><br>`;
        }).join('');

        $('.times-container').html(timesHtml);
    };

    $('#datepicker').datepicker({
        dateFormat: 'yy-mm-dd',
        onSelect: function (dateText) {
            selectedDate = dateText; // Store the selected date
            $("input[name='date']").val(dateText); // Optional: Update any form inputs if needed
            updateAvailableTimes(); // Update available times based on the new date and current lesson type
        }
    });

    /*
    $('#datepicker').datepicker({
        dateFormat: 'yy-mm-dd',
        onSelect: function (dateText) {
            selectedDate = dateText;
            console.log(availableTimesGroup)
            $("input[name='date']").val(dateText);
            var times = availableTimesInd[dateText] || [];
            var timesHtml = times.map(function (time) {
                return `<label><input type="checkbox" name="time" value="${time}" /> ${time}</label><br>`;
            }).join('');

            $('.times-container').html(timesHtml);
        }
    });
    */

    $('#lesson_type').change(function () {
        updateAvailableTimes(); // Update available times based on the current date and new lesson type
    });

    // Event delegation for dynamically added checkboxes
    $('.times-container').on('change', 'input[name="time"]', function () {
        if (this.checked) {
            // Prepare the data to be sent to the server
            $("input[name='time']").val($(this).val());
        }
    });

    /*
    $('#lesson_type').change(function () {
        var selectedOption = $(this).val();
        $.ajax({
            url: '/handle_selection',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ selectedOption: selectedOption }),
            dataType: 'json',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", $("#csrf_token").val());
            },
            success: function (response) {
                console.log(response.message);
                // You can also update the UI based on the response
            },
            error: function (xhr, status, error) {
                console.error("Error: " + error);
            }
        });
    });
    */
});