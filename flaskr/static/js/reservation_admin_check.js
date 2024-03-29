$(document).ready(function () {
    var currentPageFirstTable = 1;
    var perPageFirstTable = 3;
    var totalPagesFirstTable = 0;

    var currentPageSecondTable = 1;
    var perPageSecondTable = 5;
    var totalPagesSecondTable = 0;

    function fetchReservations(page) {
        var reservationId = $('#reservation_id').val();
        var reservation_name = $('#reservation_name').val();
        var reservation_email = $('#reservation_email').val();
        var reservation_tel_number = $('#reservation_tel_number').val();

        var baseUrl = "/reservations-api/get-reservation-details/";
        var url = baseUrl;

        if (reservationId) {
            url += "reservationID/" + reservationId;
        } else if (reservation_name) {
            url += "name/" + reservation_name;
        } else if (reservation_email) {
            url += "email/" + reservation_email;
        } else if (reservation_tel_number) {
            url += "tel-number/" + reservation_tel_number;
        }

        url += `?page=${page}&per_page=${perPageFirstTable}`;

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
                var keyOrder = ["jméno klienta", "příjmení klienta", "termín rezervace", "čas začátku", "doba výuky"]

                $.each(keyOrder, function (index, key) {
                    headerRow.append($('<th></th>').text(key));
                });
                headerRow.append($('<th></th>').text('Instruktor'));
                headerRow.append($('<th></th>').text('Platba'));
                headerRow.append($('<th></th>').text('Storno'));
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

                    var deleteButton = $(`<button class="deleteReservation" data-id="${reservation.ID_rezervace}">Storno</button>`);
                    var paymentButton = $(`<button class="markAsPaid" data-id="${reservation.ID_rezervace}">Označit zaplaceno</button>`);

                    row.append($('<td></td>').append(paymentButton));
                    row.append($('<td></td>').append(deleteButton));
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

    function fetchReservationsAll(page) {
        var baseUrl = "/reservations-api/get-reservation-details/";
        var url = baseUrl + "all";

        url += `?page=${page}&per_page=${perPageSecondTable}`;

        $.ajax({
            url: url,
            type: "GET",
            success: function (response) {
                $('#reservationDetailsAll').empty();

                if (response.reservations.length === 0) {
                    $('#reservationDetailsAll').text('No reservations found.');
                    return;
                }
                console.log(response)
                var table = $('<table></table>').addClass('reservation-table');
                var thead = $('<thead></thead>');
                var tbody = $('<tbody></tbody>');
                var headerRow = $('<tr></tr>');
                var keyOrder = ["jméno klienta", "příjmení klienta", "termín rezervace", "čas začátku", "doba výuky"]

                $.each(keyOrder, function (index, key) {
                    headerRow.append($('<th></th>').text(key));
                });
                headerRow.append($('<th></th>').text('Instruktor'));
                headerRow.append($('<th></th>').text('Platba'));
                headerRow.append($('<th></th>').text('Storno'));
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

                    var deleteButton = $(`<button class="deleteReservation" data-id="${reservation.ID_rezervace}">Storno</button>`);
                    var paymentButton = $(`<button class="markAsPaid" data-id="${reservation.ID_rezervace}">Označit zaplaceno</button>`);

                    row.append($('<td></td>').append(paymentButton));
                    row.append($('<td></td>').append(deleteButton));
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
            fetchReservationsAll(--currentPageSecondTable);
        }
    });

    $('#paginationControlsSecondTable').on('click', '#nextPageAll', function () {
        if (currentPageSecondTable < totalPagesSecondTable) {
            fetchReservationsAll(++currentPageSecondTable);
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
            url: `/reservations-api/delete-reservation-by-id/${reservationId}`,
            type: "POST",
            headers: {
                "X-CSRFToken": $('meta[name="csrf-token"]').attr('content')
            },
            success: function (response) {
                alert("Rezervace smazána.");
                fetchReservationsAll(currentPageFirstTable);
                fetchReservations(page)
            },
            error: function (xhr, status, error) {
                alert("Error");
            }
        });
    });

    $(document).on('click', '.markAsPaid', function () {
        var reservationId = $(this).data('id');
        $.ajax({
            url: `/administration/mark-reservation-paid/${reservationId}`,
            type: "POST",
            headers: {
                "X-CSRFToken": $('meta[name="csrf-token"]').attr('content')
            },
            success: function (response) {
                alert(response.message);
                fetchReservationsAll(currentPageFirstTable);
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

    fetchReservationsAll(currentPageFirstTable);
});
