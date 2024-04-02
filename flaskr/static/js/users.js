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
                fetchReservations(page)
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
                    $tbody.append('<tr><td colspan="7">No reservations found.</td></tr>');
                    return;
                }

                $.each(response.reservations, function (index, reservation) {
                    var instructorFullName = `${reservation['jméno instruktora'] || ''} ${reservation['příjmení instruktora'] || ''}`.trim();
                    var rowHtml = `<tr>
                        <td>${reservation['termín rezervace'] || 'N/A'}</td>
                        <td>${reservation['čas začátku'] || 'N/A'}</td>
                        <td>${reservation['pocet_zaku'] || 'N/A'}</td>
                        <td>${reservation['doba výuky'] || 'N/A'}</td>
                        <td>${reservation['stav platby'] || 'N/A'}</td>
                        <td>${instructorFullName || 'N/A'}</td>
                        <td></td> <!-- Placeholder for the button -->
                    </tr>`;
                    var $row = $(rowHtml);
                    var $detailButton = $(`<button class="detailReservation btn btn-primary" data-id="${reservation.ID_rezervace}">Detail rezervace</button>`);
                    $row.find('td:last').append($detailButton);
                    $tbody.append($row);
                });
                totalPagesSecondTable = response.total_pages;
                updatePaginationControlsSecondTable(totalPagesSecondTable, currentPageSecondTable);
            },
            error: function (xhr, status, error) {
                console.error("Error: " + status + " - " + error);
                $('#reservationDetailsAll').text("An error occurred while fetching the reservation details.");
            }
        });
    }





    function updatePaginationControlsSecondTable(totalPagesSecondTable, currentPageSecondTable) {
        $('#paginationControlsSecondTable').empty();
        $('#paginationControlsSecondTable').append(`<button id="prevPageAll">Previous</button>`);
        $('#paginationControlsSecondTable').append(`<button id="nextPageAll">Next</button>`);

    }

    $('#paginationControlsSecondTable').on('click', '#prevPageAll', function () {
        if (currentPageSecondTable > 1) {
            fetchReservationsAll(--currentPageSecondTable, null);
        }
    });

    $('#paginationControlsSecondTable').on('click', '#nextPageAll', function () {
        if (currentPageSecondTable < totalPagesSecondTable) {
            fetchReservationsAll(++currentPageSecondTable, null);
        }
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
                detailsHtml += '<tr><th>Doba výuky</th><td>' + response.doba_vyuky + '</td></tr>';
                detailsHtml += '<tr><th>Stav Platby</th><td>' + response.platba + '</td></tr>';
                detailsHtml += '<tr><th>Jméno a příjmení instruktora</th><td>' + response.Instructor.jmeno_instruktora + ' ' + response.Instructor.prijmeni_instruktora + '</td></tr>';
                detailsHtml += '<tr><th>Poznámka</th><td>' + response.poznamka + '</td></tr>';
                detailsHtml += '<tr><th>Počet žáků</th><td>' + response.pocet_zaku + '</td></tr>';


                var zakNames = response.Zak.map(function (zak) { return zak.jmeno_zak; }).join(', ');
                detailsHtml += '<tr><th>Žáci lekce</th><td>' + (zakNames || 'N/A') + '</td></tr>';
                detailsHtml += '</table>';

                detailsHtml += '<hr>';

                var deleteButton = $('<button class="btn btn-warning deleteReservation" data-id="' + reservationId + '">Storno</button>');
                var changeButton = $('<button class="btn btn-primary changeReservation" data-id="' + reservationId + '">Změnit rezervaci</button>');

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