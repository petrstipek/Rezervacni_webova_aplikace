/**
 * FileName: instructors_admin.js
 * Description: Script for the instructors admin page. API calling for instructors and instructor details. Deleting instructors API call.
 * Author: Petr Štípek
 * Date Created: 2024
 */

$(document).ready(function () {

    function fetchInstructors(page) {
        $.ajax({
            url: '/instructors-api/instructors-list?page=' + page,
            type: 'GET',
            dataType: 'json',
            success: function (response) {
                var instructors = response.instructors;
                var total_pages = response.total_pages;
                var current_page = response.current_page;

                $('table tbody').empty();
                $('.pagination').empty();

                $.each(instructors, function (index, instructor) {
                    $('table tbody').append('<tr><td>' + instructor.jmeno + " " + instructor.prijmeni + '</td><td><button class="btn btn-warning btn-sm button-instructor-action" data-instructor-id="' + instructor.ID_osoba + '">Zobrazit</button></td><td><button class="btn btn-danger button-instructor-delete " data-instructor-id="' + instructor.ID_osoba + '">Odstranit</button></td></tr>');
                });

                for (var i = 1; i <= total_pages; i++) {
                    $('.pagination').append('<li class="page-item ' + (i === current_page ? 'active' : '') + '"><a class="page-link" href="javascript:fetchInstructors(' + i + ')">' + i + '</a></li>');
                }
            },
            error: function (error) {
                console.log(error);
            }
        });
    }
    window.fetchInstructors = fetchInstructors;

    fetchInstructors(1);

    $('table').on('click', '.button-instructor-action', function () {
        var instructorId = $(this).data('instructor-id');
        console.log("instruktor_id", instructorId)

        $.ajax({
            url: '/instructors-api/details',
            type: 'GET',
            dataType: 'json',
            data: {
                instructor_id: instructorId
            },
            success: function (data) {
                $('#name').val(data.jmeno);
                $('#surname').val(data.prijmeni)
                $('#tel_number').val(data.tel_cislo);
                $('#email').val(data.email);
                $('#date_birth').val(data.birth_date);
                $('#date_started').val(data.start_work);
                $('#experience').val(data.seniorita);
                $('#text').val(data.popis)

            },
            error: function (xhr, status, error) {
                console.error('Error fetching instructor details:', error);
            }
        });
    });

    $('table').on('click', '.button-instructor-delete', function () {
        var instructorId = $(this).data('instructor-id');
        var csrfToken = $('meta[name="csrf-token"]').attr('content');

        $.ajax({
            url: '/instructors-api/instructors?instructor_id=' + instructorId,
            type: 'DELETE',
            dataType: 'json',
            headers: {
                "X-CSRFToken": csrfToken
            },
            success: function (response) {
                if (response.success) {
                    alert("Instruktor byl úspěšně odstraněn.");
                    //messageHtml = "Instruktor byl úspěšně odstraněn."
                    //$('#flash-messages').html(messageHtml);
                    setTimeout(function () { $('#flash-messages .alert').fadeOut(); }, 5000);
                }
                fetchInstructors(1);
            },
            error: function (xhr, status, error) {
                var errorMessage = xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : "An unknown error occurred.";
                alert("Instruktor nebyl odstrěněn. " + errorMessage);
                setTimeout(function () { $('#flash-messages .alert').fadeOut(); }, 5000);
            }
        });
    });
});