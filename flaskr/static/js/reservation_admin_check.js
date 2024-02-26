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

        var baseUrl = "/get-reservation-details/";
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

                $.each(response.reservations[0], function (key) {
                    headerRow.append($('<th></th>').text(key));
                });
                thead.append(headerRow);

                $.each(response.reservations, function (index, reservation) {
                    var row = $('<tr></tr>');
                    $.each(reservation, function (key, value) {
                        if (key === 'termin') {
                            value = formatDate(value);
                        }
                        row.append($('<td></td>').text(value));
                    });
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
        var baseUrl = "/get-reservation-details/";
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

                var table = $('<table></table>').addClass('reservation-table');
                var thead = $('<thead></thead>');
                var tbody = $('<tbody></tbody>');
                var headerRow = $('<tr></tr>');

                $.each(response.reservations[0], function (key) {
                    headerRow.append($('<th></th>').text(key));
                });
                thead.append(headerRow);

                $.each(response.reservations, function (index, reservation) {
                    var row = $('<tr></tr>');
                    $.each(reservation, function (key, value) {
                        if (key === 'termin') {
                            value = formatDate(value);
                        }
                        row.append($('<td></td>').text(value));
                    });
                    var deleteButton = $(`<button class="deleteReservation" data-id="${reservation.ID_rezervace}">Delete</button>`);
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
        $('#paginationControlsFirstTable').append(`<button id="prevPage">Previous</button>`);

        if (currentPageFirstTable > 1) {
            $('#paginationControlsFirstTable').append(`<button id="prevPage">Previous</button>`);
        }

        if (currentPageFirstTable < totalPagesFirstTable) {
            $('#paginationControlsFirstTable').append(`<button id="nextPage">Next</button>`);
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

        if (currentPageSecondTable > 1) {
            console.log("ahoj")
            $('#paginationControlsSecondTable').append(`<button id="prevPageAll">Previous</button>`);
        }

        if (currentPageSecondTable < totalPagesSecondTable) {
            $('#paginationControlsSecondTable').append(`<button id="nextPageAll">Next</button>`);
        }
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
            url: `/delete-reservation/${reservationId}`,
            type: "POST",
            headers: {
                "X-CSRFToken": $('meta[name="csrf-token"]').attr('content')
            },
            success: function (response) {
                alert("Rezervace smazána.");
                fetchReservationsAll(currentPageFirstTable);
            },
            error: function (xhr, status, error) {
                alert("Error");
            }
        });
    });

    $(document).on('click', '.markAsPaid', function () {
        var reservationId = $(this).data('id');
        $.ajax({
            url: `/mark-reservation-paid/${reservationId}`,
            type: "POST",
            headers: {
                "X-CSRFToken": $('meta[name="csrf-token"]').attr('content')
            },
            success: function (response) {
                alert("Platba uložena");
                fetchReservationsAll(currentPageFirstTable);
            },
            error: function (xhr, status, error) {
                alert("Error");
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
