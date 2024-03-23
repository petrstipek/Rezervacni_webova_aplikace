$(document).ready(function () {
    var currentPage = 1;
    var perPage = 5;
    var totalPages = 0;
    var selectedDate = null;

    $(document).on('change', '#lessonDate', function () {
        console.log("button clicked")
        selectedDate = $('#lessonDate').val();
        fetchLessons(1, selectedDate);
    });

    $('#allLessons').click(function () {
        selectedDate = null;
        $('#lessonDate').val('');
        fetchLessons(1, null);

    });

    function fetchLessons(page, date) {
        var url = `/administration-api/lessons?page=${page}&per_page=${perPage}`;
        if (date) {
            url += `&date=${date}`;
        }

        $.ajax({
            url: url,
            type: "GET",
            success: function (response) {
                console.log("Response:", response);
                $('#lessonsAll').empty();

                if (response.lessons.length === 0) {
                    $('#lessonsAll').text('Žádné lekce nejsou vypsané!');
                    return;
                }

                var table = $('<table></table>').addClass('reservation-table');
                var thead = $('<thead></thead>');
                var tbody = $('<tbody></tbody>');
                var headerRow = $('<tr></tr>');
                var keyOrder = ["Termín", "Čas začátku", "Jméno", "Příjmení", "Stav", "Typ hodiny", "Zbývající kapacita"]

                $.each(keyOrder, function (index, key) {
                    headerRow.append($('<th></th>').text(key));
                });

                headerRow.append($('<th></th>').text('Instruktor'));
                headerRow.append($('<th></th>').text('Odstranění výuky'));

                thead.append(headerRow);
                console.log(response.lessons)
                $.each(response.lessons, function (index, lesson) {
                    var row = $('<tr></tr>');
                    $.each(keyOrder, function (index, key) {
                        var value = lesson[key]
                        console.log(value)
                        if (key === 'Termín') {
                            value = formatDate(value);
                        }
                        row.append($('<td></td>').text(value));
                    });

                    var instructorFullName = lesson['Jméno'] + ' ' + lesson['Příjmení'];
                    row.append($('<td></td>').text(instructorFullName));

                    row.append($(`<td><button class="deleteReservation" onclick="deleteLesson(${lesson.ID_hodiny})">Odstranění hodiny</button></td>`));
                    tbody.append(row);
                });

                table.append(thead).append(tbody);
                $('#lessonsAll').append(table);

                totalPages = response.pages;

                updatePaginationControls(totalPages, currentPage);
            },
            error: function (xhr, status, error) {
                console.error("Error: " + status + " - " + error);
                $('#lessonsAll').text("An error occurred while fetching the reservation details.");
            }
        });
    }

    function updatePaginationControls(totalPages, currentPage) {
        $('#paginationControls').empty();

        if (currentPage > 1) {
            $('#paginationControls').append(`<button id="prevPage">Previous</button>`);
        }

        if (currentPage < totalPages) {
            $('#paginationControls').append(`<button id="nextPage">Next</button>`);
        }
    }

    $('#paginationControls').on('click', '#prevPage', function () {
        if (currentPage > 1) {
            fetchLessons(--currentPage, selectedDate);
        }
    });

    $('#paginationControls').on('click', '#nextPage', function () {
        if (currentPage < totalPages) {
            fetchLessons(++currentPage, selectedDate);
        }
    });

    window.deleteLesson = function (lessonId) {
        $.ajax({
            url: `/administration-api/lesson/${lessonId}`,
            type: "DELETE",
            headers: {
                "X-CSRFToken": $('meta[name="csrf-token"]').attr('content')
            },
            success: function (response) {
                alert(response.message);
                fetchLessons(currentPage, selectedDate);
            },
            error: function (xhr, status, error) {
                var errorMessage = "error.";
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMessage = xhr.responseJSON.message;
                }
                console.error("Error:", errorMessage);
                alert(errorMessage);
            }
        });
    }

    function formatDate(originalDateString) {
        const date = new Date(originalDateString);
        const day = date.getDate();
        const month = date.getMonth() + 1;
        const year = date.getFullYear();
        return `${day}.${month}.${year}`;
    }

    function toggleFields() {
        var selectedType = $('#lesson_type').val();
        if (selectedType === 'ind') {
            $('#div_lesson_capacity input, #div_additional_instructors input').prop('disabled', true);
            $('#div_lesson_capacity select, #div_additional_instructors select').prop('disabled', true);
        } else if (selectedType === 'group') {
            $('#div_lesson_capacity input, #div_additional_instructors input').prop('disabled', false);
            $('#div_lesson_capacity select, #div_additional_instructors select').prop('disabled', false);
        }
    }

    toggleFields();
    $('#lesson_type').change(toggleFields);

    fetchLessons(currentPage);
});