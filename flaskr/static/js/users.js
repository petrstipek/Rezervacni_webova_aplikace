$(document).ready(function () {
    var currentPageFirstTable = 1;
    var perPageFirstTable = 10;
    var totalPagesFirstTable = 0;

    var currentPageSecondTable = 1;
    var perPageSecondTable = 10;
    var totalPagesSecondTable = 0;

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
        //var baseUrl = "/administration-api/reservations";
        var queryParams = [];

        queryParams.push(`page=${page}`);
        queryParams.push(`per_page=${perPageSecondTable}`);
        if (date) {
            queryParams.push(`selected_date=${date}`)
        }
        var baseUrl = "/users-api/reservations";
        var url = baseUrl + "?" + queryParams.join("&");

        $.ajax({
            url: url,
            type: "GET",
            success: function (response) {
                $('#reservationDetailsAll').empty();

                if (response.reservations.length === 0) {
                    $('#reservationDetailsAll').text('No reservations found.');
                    return;
                }
                var table = $('<table></table>').addClass('reservation-table');
                var thead = $('<thead></thead>');
                var tbody = $('<tbody></tbody>');
                var headerRow = $('<tr></tr>');
                var keyOrder = ["termín rezervace", "čas začátku", "doba výuky", "stav platby"]

                $.each(keyOrder, function (index, key) {
                    headerRow.append($('<th></th>').text(key));
                });
                headerRow.append($('<th></th>').text('Instruktor'));
                headerRow.append($('<th></th>').text('Detail rezervace'));
                thead.append(headerRow);

                $.each(response.reservations, function (index, reservation) {
                    var row = $('<tr></tr>');
                    $.each(keyOrder, function (index, key) {
                        var value = reservation[key];
                        if (key === 'termín rezervace') {
                            value = formatDate(value);
                        }
                        row.append($('<td></td>').text(value));
                    });

                    var instructorFullName = reservation['jméno instruktora'] + ' ' + reservation['příjmení instruktora'];
                    row.append($('<td></td>').text(instructorFullName));

                    var detailbutton = $(`<button class="detailReservation btn btn-primary" id="reservationDetail" data-id="${reservation.ID_rezervace}">Detail rezervace</button>`);

                    row.append($('<td></td>').append(detailbutton));
                    tbody.append(row);
                });

                table.append(thead).append(tbody);
                $('#reservationDetailsAll').append(table);

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

                var deleteButton = $(`<button class="deleteReservation" data-id="${reservationId}">Storno</button>`);

                detailsHtml += '<table class="action-buttons-table">';
                detailsHtml += '<tr><th>Storno rezervace</th></tr>';
                detailsHtml += '<tr><td>' + deleteButton.prop('outerHTML') + '</td></tr>';
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

    $(window).click(function (event) {
        if ($(event.target).hasClass('modal')) {
            $('.modal').css('display', 'none');
            ('body').removeClass('body-no-scroll');
        }
    });

    fetchReservationsAll(currentPageFirstTable, null)
})