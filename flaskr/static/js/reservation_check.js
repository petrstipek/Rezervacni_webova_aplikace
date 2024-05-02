/**
 * FileName: reservation_check.js
 * Description: Script for the reservation check page. Building the reservation details table.
 * Author: Petr Štípek
 * Date Created: 2024
 */

$(document).ready(function () {
    $('#reservationForm').submit(function (event) {
        event.preventDefault();

        var reservationId = $('#reservation_id').val();

        $.ajax({
            url: "reservations-api/reservation/" + reservationId,
            type: "GET",
            success: function (data) {
                var reservation = data;

                $('#cell-termin').text(reservation['Termín'] || 'N/A');
                $('#cell-cas-zacatku').text(reservation['Čas začátku'] || 'N/A');
                $('#cell-pocet-zaku').text(reservation['Počet žáků'] || 'N/A');
                $('#cell-doba-vyuky').text(reservation['Doba výuky'] || 'N/A');
                $('#cell-stav-platby').text(reservation['Stav platby'] || 'N/A');
            },
            error: function (xhr, status, error) {
                console.error("Error: " + status + " - " + error);
                $('#reservationDetails').empty();
                var response = JSON.parse(xhr.responseText);
                if (response && response.error) {
                    alert("Rezervace nebyla nalezena.");
                } else {
                    alert("Rezervace nebyla nalezena.");
                }
            }
        });
    });
});