/**
 * FileName: users.js
 * Description: Script for the users page. Handling the reservation details, pagination and reservation deletion.
 * Author: Petr Štípek
 * Date Created: 2024
 */

$(document).ready(function () {
    var currentPageFirstTable = 1;
    var perPageFirstTable = 5;
    var totalPagesFirstTable = 0;

    var currentPageSecondTable = 1;
    var perPageSecondTable = 10;
    var totalPagesSecondTable = 0;

    $(document).on('click', '.deleteReservation', function () {
        var reservationId = $(this).data('id');
        $.ajax({
            url: `/administration-api/reservation/${reservationId}`,
            type: "DELETE",
            headers: {
                "X-CSRFToken": $('meta[name="csrf-token"]').attr('content')
            },
            success: function (response) {
                alert("Rezervace smazána.");
                fetchReservationsAll(currentPageFirstTable, null);
                $('#detailModal').css('display', 'none');
            },
            error: function (xhr, status, error) {
                var response = JSON.parse(xhr.responseText);
                var errorMessage = response.error;
                alert('Error, rezervace nebyla zrušena! Detail: ' + errorMessage);
            }
        });
    });

    $(document).on('change', '#reservationDate', function () {
        selectedDate = $('#reservationDate').val();
        fetchReservationsAll(1, selectedDate)
    });

    $('#allReservations').click(function () {
        selectedDate = null;
        $('#reservationDate').val('');
        fetchReservationsAll(1, null)

    });

    function fetchReservationsAll(page, date) {
        var baseUrl = "/users-api/reservations";
        var queryParams = [`page=${page}`, `per_page=${perPageFirstTable}`];
        if (date) queryParams.push(`selected_date=${date}`);
        var url = `${baseUrl}?${queryParams.join("&")}`;

        $.ajax({
            url: url,
            type: "GET",
            success: function (response) {
                var $tbody = $('#reservationDetails tbody').empty();

                if (response.reservations.length === 0) {
                    $tbody.append('<tr><td colspan="7">Žádné rezervace nenalezeny.</td></tr>');
                    return;
                }

                $.each(response.reservations, function (index, reservation) {

                    var rowHtml = `<tr>
                        <td>${reservation['rezervační kód'] || 'N/A'}</td>
                        <td>${reservation['termín rezervace'] || 'N/A'}</td>
                        <td>${reservation['čas začátku'] || 'N/A'}</td>
                        <td>${reservation['počet žáků'] || 'N/A'}</td>
                        <td>${reservation['doba výuky'] || 'N/A'}</td>
                        <td>${reservation['stav platby'] || 'N/A'}</td>
                        
                        <td></td> <!-- Placeholder for the button -->
                    </tr>`;
                    var $row = $(rowHtml);
                    var $detailButton = $(`<button class="detailReservation btn btn-primary" data-id="${reservation.ID_rezervace}">Detail rezervace</button>`);
                    $row.find('td:last').append($detailButton);

                    $tbody.append($row);
                });
                totalPagesSecondTable = response.total_pages;
                //updatePaginationControlsSecondTable(totalPagesSecondTable, currentPageSecondTable);
                updatePaginationControls(totalPagesSecondTable, currentPageSecondTable);
            },
            error: function (xhr, status, error) {
                console.error("Error: " + status + " - " + error);
                $('#reservationDetailsAll').text("An error occurred while fetching the reservation details.");
            }
        });
    }

    function updatePaginationControls(totalPages, currentPage) {
        $('#paginationControlsFirstTable').empty();

        let prevDisabled = currentPage <= 1 ? "disabled" : "";
        console.log(prevDisabled)
        $('#paginationControlsFirstTable').append(`<button id="prevPage" ${prevDisabled} onclick="${currentPage - 1}">Předchozí</button>`);

        let nextDisabled = currentPage >= totalPages ? "disabled" : "";
        $('#paginationControlsFirstTable').append(`<button id="nextPage" ${nextDisabled} onclick="${currentPage + 1}">Další</button>`);
    }

    $('#paginationControlsFirstTable').on('click', '#prevPage:not([disabled])', function () {
        fetchReservationsAll(--currentPageSecondTable, null);
    });

    $('#paginationControlsFirstTable').on('click', '#nextPage:not([disabled])', function () {
        fetchReservationsAll(++currentPageSecondTable, null);
    });

    function formatDate(originalDateString) {
        const date = new Date(originalDateString);
        const day = date.getDate();
        const month = date.getMonth() + 1;
        const year = date.getFullYear();
        return `${day}.${month}.${year}`;
    }

    $(document).on('click', '.detailReservation', function () {
        var baseUrl = "/administration-api/reservation/detail";
        var reservationId = $(this).data('id');
        $.ajax({
            url: baseUrl,
            type: 'GET',
            data: {
                reservation_id: reservationId
            },
            success: function (response) {
                var detailsHtml = '<table class="reservation-details-table">';
                detailsHtml += '<tr><th>Identifikační kód</th><td>' + response.ID_rezervace + '</td></tr>';
                detailsHtml += '<tr><th>Jméno a příjmení klienta</th><td>' + response.jmeno_klienta + ' ' + response.prijmeni_klienta + '</td></tr>';
                detailsHtml += '<tr><th>Kontakt na klienta</th><td> email: ' + response.email_klienta + ', tel. číslo: ' + response.tel_cislo_klienta + '</td></tr>';
                detailsHtml += '<tr><th>Datum rezervace</th><td>' + response.termin_rezervace + '</td></tr>';
                detailsHtml += '<tr><th>Začátek výuky</th><td>' + response.cas_zacatku + '</td></tr>';
                detailsHtml += '<tr><th>Doba výuky [počet hodin]</th><td>' + response.doba_vyuky + '</td></tr>';
                detailsHtml += '<tr><th>Stav Platby</th><td>' + response.platba + '</td></tr>';

                if (Array.isArray(response.Instructor)) {
                    var instructorNames = response.Instructor.map(function (instructor) {
                        return instructor.jmeno_instruktora + ' ' + instructor.prijmeni_instruktora;
                    });

                    var namesString = instructorNames.join(', ');

                    detailsHtml += '<tr><th>Jméno a příjmení instruktora</th><td>' + namesString + '</td></tr>';
                } else {
                    detailsHtml += '<tr><th>Jméno a příjmení instruktora</th><td>No instructors assigned</td></tr>';
                }

                detailsHtml += '<tr><th>Poznámka</th><td>' + response.poznamka + '</td></tr>';
                detailsHtml += '<tr><th>Počet žáků</th><td>' + response.pocet_zaku + '</td></tr>';


                var zakNames = response.Zak.map(function (zak) { return zak.jmeno_zak; }).join(', ');
                detailsHtml += '<tr><th>Žáci lekce</th><td>' + (zakNames || 'N/A') + '</td></tr>';
                detailsHtml += '</table>';

                detailsHtml += '<hr>';

                var deleteButton = $('<button class="btn btn-warning deleteReservation" data-id="' + reservationId + '">Storno</button>');
                var changeButton = $('<button class="btn btn-primary changeReservation" data-id="' + reservationId + '">Změnit rezervaci</button>');

                var reservationDateTime = new Date(response.termin_rezervace + 'T' + response.cas_zacatku);
                var now = new Date();
                var twoHoursLater = new Date(now.getTime() + 2 * 60 * 60 * 1000);
                var message = '';

                if (reservationDateTime <= twoHoursLater) {
                    deleteButton.prop('disabled', true);
                    changeButton.prop('disabled', true);
                    message = '<p class="reservation-warning">Reservations can only be changed or deleted more than two hours prior to the reservation time.</p>';


                    var reservationDate = new Date(response.termin_rezervace);
                    var today = new Date();
                    today.setHours(0, 0, 0, 0);

                    if (reservationDate < today) {
                        deleteButton.prop('disabled', true);
                        changeButton.prop('disabled', true);
                    }
                }

                detailsHtml += '<table class="action-buttons-table">';
                detailsHtml += '<thead>';
                detailsHtml += '<tr><th>Storno</th><th>Změnit rezervaci</th></tr>';
                detailsHtml += '</thead>';
                detailsHtml += '<tbody>';
                detailsHtml += '<td>' + deleteButton.prop('outerHTML') + '</td>';
                detailsHtml += '<td>' + changeButton.prop('outerHTML') + '</td></tr>';
                detailsHtml += '</tbody>';
                detailsHtml += '</table>';

                $('#modalBody').html(detailsHtml);

                $('#detailModal').css('display', 'block');
                $('body').addClass('body-no-scroll');
            },
            error: function (xhr, status, error) {

                $('#modalInfo').text('Error - fetchinch reservations!');
                $('#detailModal').css('display', 'block');
            }
        });
    });

    $(document).on('click', '.close', function () {
        $('#detailModal').css('display', 'none');
        $('body').removeClass('body-no-scroll');
    });

    $(document).on('click', '.changeReservation', function () {
        var reservationId = $(this).data('id');
        var targetUrl = changeReservationUrl + '?reservation_id=' + reservationId;
        window.location.href = targetUrl;
    });

    $(window).click(function (event) {
        if ($(event.target).hasClass('modal')) {
            $('.modal').css('display', 'none');
            ('body').removeClass('body-no-scroll');
        }
    });

    fetchReservationsAll(currentPageFirstTable, null)
})