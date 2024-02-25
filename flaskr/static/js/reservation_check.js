$(document).ready(function () {
    $('#reservationForm').submit(function (event) {
        event.preventDefault();

        var reservationId = $('#reservation_id').val();
        var reservation_name = $('#reservation_name').val();
        var reservation_email = $('#reservation_email').val();
        var reservation_tel_number = $('#reservation_tel_number').val();

        var baseUrl = "/get-reservation-details/";
        var url;

        if (reservationId) {
            url = baseUrl + "reservationID/" + reservationId;
        } else if (reservation_name) {
            url = baseUrl + "name/" + reservation_name;
        } else if (reservation_email) {
            url = baseUrl + "email/" + reservation_email;
        } else if (reservation_tel_number) {
            url = baseUrl + "tel-number/" + reservation_tel_number
        }

        $.ajax({
            //url: "/get-reservation-details/" + reservationId,
            url: url,
            type: "GET",
            success: function (data) {
                $('#reservationDetails').empty();
                var detailsList = $('<ul></ul>');
                $.each(data, function (key, value) {
                    detailsList.append($('<li></li>').text(key + ": " + value));
                });
                $('#reservationDetails').append(detailsList);

                var deleteButton = $('<button>Delete Reservation</button>');
                deleteButton.attr('id', 'deleteReservationButton');
                $('#reservationDetails').append(deleteButton);

                var csrfToken = $('input[name="csrf_token"]').val();

                $('#deleteReservationButton').on('click', function () {
                    if (confirm('Are you sure you want to delete this reservation?')) {
                        $.ajax({
                            url: "/delete-reservation/" + reservationId,
                            type: "DELETE",
                            beforeSend: function (xhr) {
                                xhr.setRequestHeader("X-CSRFToken", csrfToken);
                            },
                            success: function () {
                                alert('Reservation deleted successfully.');
                                $('#reservationDetails').empty();
                            },
                            error: function (xhr, status, error) {
                                console.error("Error: " + status + " - " + error);
                                alert('Failed to delete reservation.');
                            }
                        });
                    }
                });
            },
            error: function (xhr, status, error) {
                console.error("Error: " + status + " - " + error);
                $('#reservationDetails').empty();
                var response = JSON.parse(xhr.responseText);
                if (response && response.error) {
                    $('#reservationDetails').text(response.error);
                } else {
                    $('#reservationDetails').text("An error occurred while fetching the reservation details.");
                }
            }
        });
    });
});