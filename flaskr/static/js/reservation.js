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

    $('#more_students_checkbox').change(function () {
        if (this.checked) {
            $('#student_details_section').show();
        } else {
            $('#student_details_section').hide();
        }
    });

    // Parse the availableTimes data from the data-available-times attribute
    console.log("vypis tady");
    console.log($('#datepicker').data('available-times'))
    var availableTimes = ($('#datepicker').data('available-times'));
    console.log(availableTimes);
    var selectedDate = ''; // Store the selected date in a broader scope

    $('#datepicker').datepicker({
        dateFormat: 'mm/dd/yy',
        onSelect: function (dateText) {
            selectedDate = dateText; // Update selectedDate when a date is picked
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
            var dataToSend = {
                date: selectedDate,
                time: $(this).val()
            };

            // Send the data to the server using AJAX
            $.ajax({
                type: "POST",
                url: "/submit-date-time",
                contentType: "application/json",
                data: JSON.stringify(dataToSend),
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", $("input[name='csrf_token']").val());
                },
                success: function (response) {
                    console.log("Data sent successfully", response);
                },
                error: function (xhr, status, error) {
                    console.error("Error sending data", error);
                }
            });
        }
    });
});