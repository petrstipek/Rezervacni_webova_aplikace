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
            url: url,
            type: "GET",
            success: function (data) {
                $('#reservationDetails').empty();

                if (data.length === 0) {
                    $('#reservationDetails').text('No reservations found.');
                    return;
                }

                var table = $('<table></table>').addClass('reservation-table');
                var thead = $('<thead></thead>');
                var tbody = $('<tbody></tbody>');
                var headerRow = $('<tr></tr>');

                $.each(data[0], function (key) {
                    headerRow.append($('<th></th>').text(key));
                });
                thead.append(headerRow);

                $.each(data, function (index, reservation) {
                    var row = $('<tr></tr>');
                    $.each(reservation, function (key, value) {
                        row.append($('<td></td>').text(value));
                    });

                    var deleteButton = $('<button>Delete Reservation</button>')
                        .addClass('deleteReservationButton')
                        .data('reservationId', reservation.ID_rezervace);
                    row.append($('<td></td>').append(deleteButton));

                    tbody.append(row);
                });

                table.append(thead).append(tbody);
                $('#reservationDetails').append(table);

                $(document).on('click', '.deleteReservationButton', function () {
                    var reservationId = $(this).data('reservationId');

                    if (confirm('Are you sure you want to delete this reservation?')) {
                        var csrfToken = $('input[name="csrf_token"]').val();

                        $.ajax({
                            url: "/delete-reservation/" + reservationId,
                            type: "DELETE",
                            beforeSend: function (xhr) {
                                xhr.setRequestHeader("X-CSRFToken", csrfToken);
                            },
                            success: function () {
                                alert('Reservation deleted successfully.');
                                $(this).closest('tr').remove();
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