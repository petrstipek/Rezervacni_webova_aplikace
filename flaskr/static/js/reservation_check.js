$(document).ready(function () {
    $('#reservationForm').submit(function (event) {
        event.preventDefault();

        var reservationId = $('#reservation_id').val();
        var reservation_name = $('#reservation_name').val();
        var reservation_email = $('#reservation_email').val();
        var reservation_tel_number = $('#reservation_tel_number').val();

        var baseUrl = "/reservations-api/get-reservation-details/";
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
            url: "reservations-api/get-reservation/" + reservationId,
            type: "GET",
            success: function (data) {
                var reservation = data;
                $('#reservationDetails').empty();
                var keyOrder = ['Termín', 'Čas začátku', 'Počet žáků', 'Doba výuky', 'Stav platby'];

                var table = $('<table></table>').addClass('reservation-table');
                var tbody = $('<tbody></tbody>');

                $.each(keyOrder, function (index, key) {
                    var value = reservation[key];
                    var row = $('<tr></tr>');
                    row.append($('<th></th>').text(key));
                    row.append($('<td></td>').text(value));
                    tbody.append(row);
                });

                var deleteRow = $('<tr></tr>');
                var deleteCell = $('<td></td>').attr('colspan', '2');
                var deleteButton = $('<button>Delete Reservation</button>')
                    .addClass('deleteReservationButton')
                    .data('reservationId', reservation['ID_rezervace']);
                deleteCell.append(deleteButton);
                deleteRow.append(deleteCell);
                tbody.append(deleteRow);

                table.append(tbody);
                $('#reservationDetails').append(table);
            },
            error: function (xhr, status, error) {
                console.error("Error: " + status + " - " + error);
                $('#reservationDetails').empty();
                var response = JSON.parse(xhr.responseText);
                if (response && response.error) {
                    $('#reservationDetails').text(response.error);
                } else {
                    $('#reservationDetails').text("Error!");
                }
            }
        });
    });

    $(document).on('click', '.deleteReservationButton', function () {
        var reservationId = $('#reservation_id').val();
        if (confirm('Opravdu chcete zrušit svou rezervaci?')) {
            var csrfToken = $('input[name="csrf_token"]').val();

            $.ajax({
                url: "/reservations-api/delete-reservation-by-code/" + reservationId,
                type: "DELETE",
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                },
                success: function () {
                    alert('Rezervace zrušena!');
                    location.reload();
                },
                error: function (xhr, status, error) {
                    console.error("Error: " + status + " - " + error);
                    alert('Error, rezervace nebyla zrušena!');
                }
            });
        }
    });
});