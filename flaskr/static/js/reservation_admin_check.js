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
                var $tbody = $('.reservation-table tbody');
                $tbody.empty();

                if (response.reservations.length === 0) {
                    $tbody.append('<tr><td colspan="8">No reservations found.</td></tr>');
                    return;
                }

                response.reservations.forEach(function (reservation, index) {
                    if (index < 10) {
                        var row = $('<tr></tr>');
                        row.append($('<td></td>').text(reservation['jméno klienta'] || 'N/A'));
                        row.append($('<td></td>').text(reservation['příjmení klienta'] || 'N/A'));
                        row.append($('<td></td>').text(reservation['termín rezervace'] || 'N/A'));
                        row.append($('<td></td>').text(reservation['čas začátku'] || 'N/A'));
                        row.append($('<td></td>').text(reservation['doba výuky'] || 'N/A'));
                        row.append($('<td></td>').text(reservation['stav platby'] || 'N/A'));
                        var instructorFullName = (reservation['jméno instruktora'] || '') + ' ' + (reservation['příjmení instruktora'] || '');
                        row.append($('<td></td>').text(instructorFullName.trim() || 'N/A'));
                        var detailButton = $(`<button class="detailReservation btn btn-primary" data-id="${reservation.ID_rezervace}">Detail rezervace</button>`);
                        row.append($('<td></td>').append(detailButton));

                        $tbody.append(row);
                    }
                });
                var rowsToAdd = Math.max(0, 10 - response.reservations.length);
                for (let i = 0; i < rowsToAdd; i++) {
                    $tbody.append('<tr><td colspan="8"></td></tr>');
                }
                currentPageFirstTable = response.current_page;
                totalPagesFirstTable = response.total_pages;

                updatePaginationControlsFirstTable(totalPagesFirstTable, currentPageFirstTable);
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
            queryParams.push(`selected_date=${date}`);
        }
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
                var keyOrder = ["jméno klienta", "příjmení klienta", "termín rezervace", "čas začátku", "doba výuky", "stav platby"];

                $.each(keyOrder, function (index, key) {
                    headerRow.append($('<th></th>').text(key));
                });
                headerRow.append($('<th></th>').text('Instruktor'));
                headerRow.append($('<th></th>').text('Detail rezervace'));
                thead.append(headerRow);

                $.each(response.reservations, function (index, reservation) {
                    var row = $('<tr></tr>');
                    $.each(keyOrder, function (i, key) {
                        var value = reservation[key] || '';
                        if (key === 'termín rezervace') {
                            value = formatDate(value);
                        }
                        row.append($('<td></td>').text(value));
                    });

                    var instructorFullName = reservation['jméno instruktora'] + ' ' + reservation['příjmení instruktora'];
                    row.append($('<td></td>').text(instructorFullName));

                    var detailbutton = $(`<button class="detailReservation btn btn-primary" data-id="${reservation.ID_rezervace}">Detail rezervace</button>`);
                    row.append($('<td></td>').append(detailbutton));

                    tbody.append(row);
                });

                var rowsToAdd = perPageFirstTable - response.reservations.length;
                for (var i = 0; i < rowsToAdd; i++) {
                    tbody.append('<tr><td colspan="' + (keyOrder.length + 2) + '">&nbsp;</td></tr>');
                }

                table.append(thead).append(tbody);
                $('#reservationDetailsAll').append(table);

                totalPagesSecondTable = response.total_pages;
                updatePaginationControlsFirstTable(totalPagesSecondTable, currentPageSecondTable);
            },
            error: function (xhr, status, error) {
                console.error("Error: " + status + " - " + error);
                $('#reservationDetailsAll').text("An error occurred while fetching the reservation details.");
            }
        });
    }


    function updatePaginationControlsFirstTable(totalPagesFirstTable, currentPageFirstTable) {
        $('#paginationControlsFirstTable').empty();

        let prevDisabled = currentPageFirstTable <= 1 ? "disabled" : "";
        $('#paginationControlsFirstTable').append(`<button id="prevPage" ${prevDisabled} onclick="${currentPageFirstTable - 1}">Předchozí</button>`);

        let nextDisabled = currentPageFirstTable >= totalPagesFirstTable ? "disabled" : "";
        $('#paginationControlsFirstTable').append(`<button id="nextPage" ${nextDisabled} onclick="${currentPageFirstTable + 1}">Další</button>`);
    }

    $('#paginationControlsFirstTable').on('click', '#prevPage:not([disabled])', function () {
        fetchReservations(--currentPageFirstTable);
    });

    $('#paginationControlsFirstTable').on('click', '#nextPage:not([disabled])', function () {
        fetchReservations(++currentPageFirstTable);
    });
    //-----
    /*
    function updatePaginationControlsSecondTable(totalPagesSecondTable, currentPageSecondTable) {
        console.log("jsem spustedn")
        $('#paginationControlsSecondTable').empty();

        let prevDisabled = currentPageSecondTable <= 1 ? "disabled" : "";
        $('#paginationControlsSecondTable').append(`<button id="prevPage" ${prevDisabled} onclick="changePage(${currentPageSecondTable - 1})">Předchozí</button>`);

        let nextDisabled = currentPageSecondTable >= totalPagesSecondTable ? "disabled" : "";
        $('#paginationControlsSecondTable').append(`<button id="nextPage" ${nextDisabled} onclick="changePage(${currentPageSecondTable + 1})">Další</button>`);
    }

    $('#paginationControlsSecondTable').on('click', '#prevPage:not([disabled])', function () {
        fetchReservations(--currentPageSecondTable);
    });

    $('#paginationControlsSecondTable').on('click', '#nextPage:not([disabled])', function () {
        fetchReservations(++currentPageSecondTable);
    });


    /*
    function updatePaginationControlsSecondTable(totalPagesSecondTable, currentPageSecondTable) {
        $('#paginationControlsSecondTable').empty();
        $('#paginationControlsSecondTable').append(`<button id="prevPageAll">Předchozí</button>`);
        $('#paginationControlsSecondTable').append(`<button id="nextPageAll">Další</button>`);

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
    */
    //-----
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

    $(document).on('click', '.markEmergency', function () {
        var baseUrl = "/administration-api/reservation/emergency";

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
                //fetchReservationsAll(currentPageFirstTable, null);
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
    $(document).on('change', '#newDate', function () {
        fetchAvailableTimes();
    });

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
                detailsHtml += '<tr><th>Jazyk lekce</th><td>' + response.jazyk + '</td></tr>';
                detailsHtml += '<tr><th>Počet žáků</th><td>' + response.pocet_zaku + '</td></tr>';


                var zakNames = response.Zak.map(function (zak) { return zak.jmeno_zak; }).join(', ');
                var zakExperiences = response.Zak.map(function (zak) { return zak.zkusenost_zak; }).join(', ');
                var zakAges = response.Zak.map(function (zak) { return zak.vek_zak; }).join(', ');
                var emergency = response.Instruktor_emergency.map(function (instruktor) { return instruktor.pohotovost; }).join(', ');
                detailsHtml += '<tr><th>Žáci lekce</th><td>' + (zakNames || 'N/A') + '</td></tr>';
                detailsHtml += '<tr><th>Zkušenosti žáků</th><td>' + (zakExperiences || 'N/A') + '</td></tr>';
                detailsHtml += '<tr><th>Věk žáků</th><td>' + (zakAges || 'N/A') + '</td></tr>';
                detailsHtml += '<tr><th>Pohotovost instruktora</th><td>' + (emergency || 'není pohotovost') + '</td></tr>';

                detailsHtml += '</table>';

                detailsHtml += '<hr>';

                var deleteButton = $('<button class="btn btn-warning deleteReservation" data-id="' + reservationId + '">Storno</button>');
                var paymentButton = $('<button class="btn btn-warning markAsPaid" data-id="' + reservationId + '">Označit zaplaceno</button>');
                var changeButton = $('<button class="btn btn-primary changeReservation" data-id="' + reservationId + '">Změnit rezervaci</button>');
                var instructorButton = $('<button class="btn btn-primary markEmergency" data-id="' + reservationId + '">Pohotovost instruktor</button>');

                detailsHtml += '<table class="action-buttons-table">';
                detailsHtml += '<thead>';
                detailsHtml += '<tr><th>Zaplatit</th><th>Storno</th><th>Pohotovost instruktor</th><th>Změnit</th></tr>';
                detailsHtml += '</thead>';
                detailsHtml += '<tbody>';
                detailsHtml += '<tr><td>' + paymentButton.prop('outerHTML') + '</td>';
                detailsHtml += '<td>' + deleteButton.prop('outerHTML') + '</td>';
                detailsHtml += '<td>' + instructorButton.prop('outerHTML') + '</td>';
                detailsHtml += '<td>' + changeButton.prop('outerHTML') + '</td></tr>';
                detailsHtml += '</tbody>';
                detailsHtml += '</table>';


                $('#modalBody').html(detailsHtml);

                $('#detailModal').css('display', 'block');
                $('body').addClass('body-no-scroll');
            },
            error: function (xhr, status, error) {

                $('#modalInfo').text('Error - fetching reservations!');
                $('#detailModal').css('display', 'block');
            }
        });
    });

    function updateAvailableTimes(data) {
        selectedDate = $('#newDate').val();
        var timesForDate = data[selectedDate];
        if (!timesForDate) {
            $('#newTime').html('<option value="">Žádné dostupné časy</option>');
            return;
        }

        var timeOptions = '<option value="">Vyberte čas</option>';
        $.each(timesForDate, function (index, timeInfo) {
            var time = timeInfo[0];
            var capacity = timeInfo[1];
            timeOptions += `<option value="${time}">${time} (Kapacita: ${capacity})</option>`;
        });
        $('#newTime').html(timeOptions);
    }

    function fetchAvailableTimes() {
        const instructorId = 0
        $.ajax({
            url: '/reservations-api/lessons/' + instructorId + '/available-times',
            type: 'GET',
            success: function (data) {
                updateAvailableTimes(data)
            },
            error: function (error) {
                console.error('Error fetching available times:', error);
            }
        });
    }

    $(document).on('click', '.close', function () {
        $('#detailModal').css('display', 'none');
        $('body').removeClass('body-no-scroll');
    });

    $(window).click(function (event) {
        if ($(event.target).hasClass('modal')) {
            $('.modal').css('display', 'none');
            //('body').removeClass('body-no-scroll');
        }
    });

    const formattedDate = todayDate()
    $('#reservationDate').val(formattedDate);
    fetchReservationsAll(currentPageFirstTable, formattedDate);

    $(document).on('click', '.changeReservation', function () {
        var reservationId = $(this).data('id');
        var targetUrl = changeReservationUrl + '?reservation_id=' + reservationId;
        window.location.href = targetUrl;
    });

});
