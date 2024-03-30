$(document).ready(function () {

    $('.button-instructor-action').click(function () {
        var instructorId = $(this).data('instructor-id');

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

            },
            error: function (xhr, status, error) {
                console.error('Error fetching instructor details:', error);
            }
        });
    });
});