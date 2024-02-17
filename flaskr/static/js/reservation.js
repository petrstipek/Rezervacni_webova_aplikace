$(document).ready(function () {

    function toggleRequired(clientNumber) {
        const fields = [
            $(`#surname_client${clientNumber}`),
            $(`#age_client${clientNumber}`),
            $(`#experience_client${clientNumber}`)
        ];
        // Check if the name field is filled out
        const isNameFilled = $(`#name_client${clientNumber}`).val().trim() !== '';

        // Set the required attribute based on if the name field is filled
        fields.forEach($field => {
            if (isNameFilled) {
                $field.attr('required', 'required');
            } else {
                $field.removeAttr('required');
            }
        });
    }

    // Event listeners for each client name field
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


    var availableTimes = ($('#datepicker').data('available-times'));
    var selectedDate = '';

    $('#datepicker').datepicker({
        dateFormat: 'yy-mm-dd',
        onSelect: function (dateText) {
            selectedDate = dateText;
            $("input[name='date']").val(dateText);
            var times = availableTimes[dateText] || [];
            var timesHtml = times.map(function (time) {
                return `<label><input type="checkbox" name="time" value="${time}" /> ${time}</label><br>`;
            }).join('');

            $('.times-container').html(timesHtml);
        }
    });

    // Event delegation for dynamically added checkboxes
    $('.times-container').on('change', 'input[name="time"]', function () {
        if (this.checked) {
            // Prepare the data to be sent to the server
            $("input[name='time']").val($(this).val());
        }
    });
});