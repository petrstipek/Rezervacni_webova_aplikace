$(document).ready(function () {
    var currentPage = 1;
    var perPage = 7;
    var totalPages = 0;
    var selectedDate = null;

    const lessonTypeSelect = document.getElementById('lesson_type');
    const additionalField1Container = document.getElementById('div_lesson_capacity');
    const additionalField2Container = document.getElementById('div_additional_instructors');

    lessonTypeSelect.addEventListener('change', function () {
        if (this.value === 'ind') {
            additionalField1Container.style.display = 'none';
            additionalField2Container.style.display = 'none';
        } else if (this.value === 'group') {
            additionalField1Container.style.display = '';
            additionalField2Container.style.display = '';
        }
    });

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
        var url = `/admin-api-lessons/get-lessons?page=${page}&per_page=${perPage}`;
        if (date) {
            url += `&date=${date}`;
        }
        console.log("Request URL:", url);

        $.ajax({
            url: url,
            type: "GET",
            success: function (response) {
                console.log("Response:", response);
                $('#lessonsAll').empty();

                if (response.lessons.length === 0) {
                    $('#lessonsAll').text('Žádné lekce nejsou vypsané');
                    return;
                }

                var table = $('<table></table>').addClass('lessons-table');
                var thead = $('<thead></thead>');
                var tbody = $('<tbody></tbody>');
                var headerRow = $('<tr></tr>');

                $.each(response.lessons[0], function (key) {
                    headerRow.append($('<th></th>').text(key));
                });
                thead.append(headerRow);

                $.each(response.lessons, function (index, lesson) {
                    var row = $('<tr></tr>');
                    $.each(lesson, function (key, value) {
                        if (key === 'datum') {
                            value = formatDate(value);
                        }
                        row.append($('<td></td>').text(value));
                    });
                    row.append($(`<td><button onclick="deleteLesson(${lesson.ID_hodiny})">Smazání hodiny</button></td>`));
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
            url: `/administration/delete_lesson_admin/` + lessonId,
            type: "POST",
            headers: {
                "X-CSRFToken": $('meta[name="csrf-token"]').attr('content')
            },
            success: function (response) {
                alert("success");
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

    fetchLessons(currentPage);
});