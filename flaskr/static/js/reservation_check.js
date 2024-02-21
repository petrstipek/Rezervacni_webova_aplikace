$(document).ready(function () {
    $('#reservationForm').submit(function (event) {
        event.preventDefault();

        var reservationId = $('#reservation_id').val();

        $.ajax({
            url: "/get-reservation-details/" + reservationId,
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