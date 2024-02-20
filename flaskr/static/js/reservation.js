$(document).ready(function () {


    function fetchAvailableTimes() {
        console.log("spusteno")
        var instructorId = $('#lesson_instructor').val();
        var lessonType = $('#lesson_type').val(); // Get selected lesson type

        if (lessonType === 'individual' && instructorId) {
            $.ajax({
                url: '/get-available-times/individual/' + instructorId,
                type: 'GET',
                success: function (data) {
                    console.log("uz jsem tady konecne")
                    console.log(data)
                    console.log(data["2024-02-22"])
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








    /*
        $('#lesson_instructor').change(function () {
            var instructorId = $(this).val();
            $.ajax({
                url: '/get-available-times/' + instructorId,
                type: 'GET',
                success: function (data) {
                    console.log("get-available-times")
                    console.log(data)
                    // Assuming 'data' is a list of strings representing available times
                    // Update your date picker with these times
                    //updateDatePicker(data);
                },
                error: function (error) {
                    console.log(error);
                }
            });
        });
        */

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

    /*
    function updateAvailableTimes(data_times) {
        if (!selectedDate) {
            return;
        }

        //var lessonType = $('#lesson_type').val();

        //var times = lessonType === 'individual' ? availableTimesInd[selectedDate] : availableTimesGroup[selectedDate];


        console.log("data times tady")
        console.log(data_times)
        data_times = JSON.parse(data_times)
        data_times = data_times || [];

        var timesForSelectedDate = data_times[selectedDate];

        if (!data_times[selectedDate]) {
            console.log("No times for selected date:", selectedDate);
            $('.times-container').html("No available times for selected date.");
            return;
        }
        


        var timesHtml = timesForSelectedDate.map(function (timeCountPair) {
            // timeCountPair is like ["11:00", 2]
            var time = timeCountPair[0]; // Extract the time part
            var count = timeCountPair[1]; // Extract the count part (if you want to display it)
            return `<label><input type="checkbox" name="time" value="${time}" /> ${time} (Available Slots: ${count})</label><br>`;
        }).join('');

        $('.times-container').html(timesHtml);
    };
    */

    function updateAvailableTimes(data_times) {
        // Ensure selectedDate and data_times are defined
        if (!selectedDate || typeof data_times === 'undefined') {
            console.log("selectedDate or data_times is undefined.");
            return;
        }

        selectedDate = selectedDate.trim();
        console.log("Selected date:", selectedDate);
        console.log("Data times:", data_times);
        console.log("Type of selectedDate:", typeof selectedDate);




        // Safeguard for data_times[selectedDate]
        if (!data_times.hasOwnProperty(selectedDate)) {
            console.log("No available times for the selected date:", selectedDate);
            $('.times-container').html("No available times for selected date.");
            return;
        }

        var timesForSelectedDate = data_times[selectedDate];

        if (!Array.isArray(timesForSelectedDate)) {
            console.log("Times for selected date is not an array:", timesForSelectedDate);
            return;
        }

        var timesHtml = timesForSelectedDate.map(function (timeCountPair) {
            var time = timeCountPair[0]; // Extract the time string
            return `<label><input type="checkbox" name="time" value="${time}" /> ${time}</label><br>`;
        }).join('');

        $('.times-container').html(timesHtml);
    }

    $('#datepicker').datepicker({
        dateFormat: 'yy-mm-dd',
        onSelect: function (dateText) {
            selectedDate = dateText; // Store the selected date
            $("input[name='date']").val(dateText); // Optional: Update any form inputs if needed
            updateAvailableTimes(fetchAvailableTimes()); // Update available times based on the new date and current lesson type
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

    /*
    $('#lesson_type').change(function () {
        updateAvailableTimes(); // Update available times based on the current date and new lesson type
    });
    */

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