$(document).ready(function () {
    var currentPage = 1;
    var perPage = 7;
    var totalPages = 0;
    var selectedDate = null;

    $(".close").click(function () {
        $("#detailModal").hide();
        $("body").css("overflow", "auto");
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
        var url = `/administration-api/lessons?page=${page}&per_page=${perPage}`;
        if (date) {
            url += `&date=${date}`;
        }

        $.ajax({
            url: url,
            type: "GET",
            success: function (response) {
                console.log("Response:", response);

                var $tbody = $('.reservation-table tbody');
                $tbody.find('tr').each(function (index) {
                    if (index < 7) {
                        $(this).find('td').empty().removeAttr('colspan');
                    }
                });

                if (response.lessons.length === 0) {
                    $tbody.find('tr:first').html('<td colspan="8">Žádné lekce nejsou vypsané!</td>');
                    return;
                }

                response.lessons.forEach(function (lesson, index) {
                    if (index < 7) {
                        var $row = $tbody.find('tr').eq(index);
                        var cellsHtml = `
                            <td>${lesson.Termín}</td>
                            <td>${lesson['Čas začátku']}</td>
                            <td>${lesson.Stav}</td>
                            <td>${lesson['Typ hodiny']}</td>
                            <td>${lesson['Zbývající kapacita'] || 'N/A'}</td>
                            <td>${lesson.Jméno + ' ' + lesson.Příjmení}</td>
                            <td><button class="deleteReservation" onclick="deleteLesson(${lesson.ID_hodiny})">Odstranění hodiny</button></td>
                            <td><button class="detailLesson btn btn-primary" data-id="${lesson.ID_hodiny}">Detail hodiny</button></td>
                        `;
                        $row.html(cellsHtml);
                    }
                });

                for (let i = response.lessons.length; i < 7; i++) {
                    var $emptyRow = $tbody.find('tr').eq(i);
                    if ($emptyRow.length === 0) {
                        $emptyRow = $('<tr><td colspan="8"></td></tr>').appendTo($tbody);
                    } else {
                        $emptyRow.html('<td colspan="8"></td>');
                    }
                }

                totalPages = response.pages;
                updatePaginationControls(totalPages, currentPage);
            },
            error: function (xhr, status, error) {
                console.error("Error: " + status + " - " + error);
                $tbody.html('<tr><td colspan="8">Error fetching lesson details.</td></tr>');
            }
        });
    }

    function updatePaginationControls(totalPages, currentPage) {
        $('#paginationControlsFirstTable').empty();

        let prevDisabled = currentPage <= 1 ? "disabled" : "";
        $('#paginationControlsFirstTable').append(`<button id="prevPage" ${prevDisabled} onclick="${currentPage - 1}">Předchozí</button>`);

        let nextDisabled = currentPage >= totalPages ? "disabled" : "";
        $('#paginationControlsFirstTable').append(`<button id="nextPage" ${nextDisabled} onclick="${currentPage + 1}">Další</button>`);
    }

    $('#paginationControlsFirstTable').on('click', '#prevPage:not([disabled])', function () {
        fetchLessons(--currentPage, selectedDate);
    });

    $('#paginationControlsFirstTable').on('click', '#nextPage:not([disabled])', function () {
        fetchLessons(++currentPage, selectedDate);
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

    $(document).on('click', '.detailLesson', function () {
        var lessonId = $(this).data('id');
        loadAndShowLessonDetails(lessonId);
    });

    toggleFields();
    $('#lesson_type').change(toggleFields);

    fetchLessons(currentPage);
});

function loadAndShowLessonDetails(lessonId) {
    var baseUrl = "/administration-api/lesson-detail";
    $.ajax({
        url: baseUrl,
        type: 'GET',
        data: { lesson_id: lessonId },
        success: function (response) {
            console.log("Response:", response);

            var detailsHtml = `<table class="reservation-details-table">
                <tr><th>ID hodiny</th><td>${response.ID_hodiny}</td></tr>
                <tr><th>Datum</th><td>${response.datum}</td></tr>
                <tr><th>Čas začátku</th><td>${response.cas_zacatku}</td></tr>
                <tr><th>Stav</th><td>${response.stav}</td></tr>
                <tr><th>Typ hodiny</th><td>${response.typ_hodiny}</td></tr>
                <tr><th>Obsazenost</th><td>${response.obsazenost}</td></tr>
                <tr><th>Kapacita</th><td>${response.kapacita}</td></tr>
            </table>`;

            $('#modalBody').html(detailsHtml);
            $('#detailModal').css('display', 'block');
            $('body').addClass('body-no-scroll');

            $('input[name="lesson_id"]').val(response.ID_hodiny);

            if (response.typ_hodiny === 'ind') {
                $('#kapacitaField').prop('disabled', true);
            } else {
                $('#instructor').prop('disabled', true);
                $('#kapacitaField').prop('disabled', false);
            }
        },
        error: function (xhr, status, error) {
            $('#modalInfo').text('Error - fetching lesson details!');
            $('#detailModal').css('display', 'block');
        }
    });
}

$('#time_start').multiselect({
    enableFiltering: false,
    includeSelectAllOption: true,
    nonSelectedText: 'Select Times',
    buttonWidth: '100%',
    selectAllText: 'Vybrat vše',
    nonSelectedText: 'Vyberte termín',
    allSelectedText: 'Vše vybráno',
    nSelectedText: 'termíny zvoleny',
});

$(document).ready(function () {
    function toggleAdditionalParameters() {
        var selectedType = $('#lesson_type').val();
        $('#div_lesson_capacity').hide();
        $('#div_additional_instructors').hide();

        if (selectedType === 'ind') {
            $('#div_additional_instructors').slideUp();
            $('#div_lesson_capacity').slideUp();
        } else if (selectedType === 'group') {
            $('#div_lesson_capacity').slideDown();
            $('#div_additional_instructors').slideDown();
        }
    }
    toggleAdditionalParameters();
    $('#lesson_type').change(function () {
        toggleAdditionalParameters();
    });
});