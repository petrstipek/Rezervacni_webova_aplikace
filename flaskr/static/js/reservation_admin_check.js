$(document).ready(function () {
    var currentPageFirstTable = 1;
    var perPageFirstTable = 10;
    var totalPagesFirstTable = 0;

    var currentPageSecondTable = 1;
    var perPageSecondTable = 5;
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

    function fetchReservations(page) {
        var reservationId = $('#reservation_id').val();
        var reservation_name = $('#reservation_name').val();
        var reservation_email = $('#reservation_email').val();
        var reservation_tel_number = $('#reservation_tel_number').val();

        var baseUrl = "/administration-api/reservations";
        var queryParams = [];

        if (reservationId) {
            queryParams.push("reservation_id=" + encodeURIComponent(reservationId));
        }
        if (reservation_name) {
            queryParams.push("name=" + encodeURIComponent(reservation_name));
        }
        if (reservation_email) {
            queryParams.push("email=" + encodeURIComponent(reservation_email));
        }
        if (reservation_tel_number) {
            queryParams.push("tel_number=" + encodeURIComponent(reservation_tel_number));
        }

        queryParams.push(`page=${page}`);
        queryParams.push(`per_page=${perPageFirstTable}`);

        var url = baseUrl + "?" + queryParams.join("&");

        $.ajax({
            url: url,
            type: "GET",
            success: function (response) {
                $('#reservationDetails').empty();

                if (response.reservations.length === 0) {
                    $('#reservationDetails').text('No reservations found.');
                    return;
                }

                var table = $('<table></table>').addClass('reservation-table');
                var thead = $('<thead></thead>');
                var tbody = $('<tbody></tbody>');
                var headerRow = $('<tr></tr>');
                var keyOrder = ["jméno klienta", "příjmení klienta", "termín rezervace", "čas začátku", "doba výuky", "stav platby"]

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
                $('#reservationDetails').append(table);

                totalPagesFirstTable = response.total_pages;

                updatePaginationControlsFirstTable(totalPagesFirstTable, page);
            },
            error: function (xhr, status, error) {
                console.error("Error: " + status + " - " + error);
                $('#reservationDetails').text("An error occurred while fetching the reservation details.");
            }
        });
    }

    function fetchReservationsAll(page, date) {
        var baseUrl = "/administration-api/reservations";
        var queryParams = [];

        queryParams.push(`page=${page}`);
        queryParams.push(`per_page=${perPageFirstTable}`);
        if (date) {
            queryParams.push(`selected_date=${date}`)
        }
        var url = baseUrl + "?" + queryParams.join("&");
        var baseUrl = "/administration-api/reservations/";

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
                var keyOrder = ["jméno klienta", "příjmení klienta", "termín rezervace", "čas začátku", "doba výuky", "stav platby"]

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

    function updatePaginationControlsFirstTable(totalPagesFirstTable, currentPageFirstTable) {
        $('#paginationControlsFirstTable').empty();

        if (currentPageFirstTable > 1) {
            $('#paginationControlsFirstTable').append(`<button id="prevPage" onclick="changePage(${currentPageFirstTable - 1})">Previous</button>`);
        }

        if (currentPageFirstTable < totalPagesFirstTable) {
            $('#paginationControlsFirstTable').append(`<button id="nextPage" onclick="changePage(${currentPageFirstTable + 1})">Next</button>`);
        }
    }

    $('#paginationControlsFirstTable').on('click', '#prevPage', function () {
        if (currentPageFirstTable > 1) {
            fetchReservations(--currentPageFirstTable);
        }
    });

    $('#paginationControlsFirstTable').on('click', '#nextPage', function () {
        if (currentPageFirstTable < totalPagesFirstTable) {
            fetchReservations(++currentPageFirstTable);
        }
    });

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

    $('#reservationForm').submit(function (event) {
        event.preventDefault();
        currentPageFirstTable = 1;
        fetchReservations(currentPageFirstTable);
    });

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

    $(document).on('click', '.markAsPaid', function () {
        var baseUrl = "/administration-api/reservation/payment";
        var queryParams = [];
        var reservationId = $(this).data('id');
        queryParams.push("reservation_id=" + encodeURIComponent(reservationId))

        var url = baseUrl + "?" + queryParams.join("&");

        $.ajax({
            url: url,
            type: "POST",
            headers: {
                "X-CSRFToken": $('meta[name="csrf-token"]').attr('content')
            },
            success: function (response) {
                alert(response.message);
                fetchReservationsAll(currentPageFirstTable, null);
                $('.detailReservation[data-id="' + reservationId + '"]').trigger('click');
            },
            error: function (xhr, status, error) {
                if (xhr.responseJSON) {
                    alert(xhr.responseJSON.message);
                } else {
                    alert("Error: " + error);
                }
            }
        });
    });

    function formatDate(originalDateString) {
        const date = new Date(originalDateString);
        const day = date.getDate();
        const month = date.getMonth() + 1;
        const year = date.getFullYear();
        return `${day}.${month}.${year}`;
    }

    function todayDate() {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        const formattedDate = `${year}-${month}-${day}`;
        return formattedDate
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
                detailsHtml += '<tr><th>Datum rezervace</th><td>' + response.termin_rezervace + '</td></tr>';
                detailsHtml += '<tr><th>Začátek výuky</th><td>' + response.cas_zacatku + '</td></tr>';
                detailsHtml += '<tr><th>Doba výuky</th><td>' + response.doba_vyuky + '</td></tr>';
                detailsHtml += '<tr><th>Stav Platby</th><td>' + response.platba + '</td></tr>';
                detailsHtml += '<tr><th>Jméno a příjmení instruktora</th><td>' + response.Instructor.jmeno_instruktora + ' ' + response.Instructor.prijmeni_instruktora + '</td></tr>';

                var zakNames = response.Zak.map(function (zak) { return zak.jmeno_zak; }).join(', ');
                detailsHtml += '<tr><th>Žáci lekce</th><td>' + (zakNames || 'N/A') + '</td></tr>';
                detailsHtml += '</table>';

                detailsHtml += '<hr>';

                var deleteButton = $(`<button class="deleteReservation" data-id="${reservationId}">Storno</button>`);
                var paymentButton = $(`<button class="markAsPaid" data-id="${reservationId}">Označit zaplaceno</button>`);

                detailsHtml += '<table class="action-buttons-table">';
                detailsHtml += '<tr><th>Zaplatit</th><th>Odstranit</th></tr>';
                detailsHtml += '<tr><td>' + paymentButton.prop('outerHTML') + '</td><td>' + deleteButton.prop('outerHTML') + '</td></tr>';
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


    const formattedDate = todayDate()
    $('#reservationDate').val(formattedDate);
    fetchReservationsAll(currentPageFirstTable, formattedDate);
});
