$(document).ready(function () {
    function school_information() {
        $.ajax({
            url: '/administration-api/school/information',
            type: 'GET',
            success: function (data) {
                updateReservationChart(data.dates, data.reservation_counts);
            },
            error: function (error) {
                console.error('Error fetching school information:', error);
            }
        });
    }

    school_information();

    function updateReservationChart(dates, reservationCounts) {
        var ctx = document.getElementById('reservationChart').getContext('2d');
        var reservationChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Reservations in the last 7 days',
                    data: reservationCounts,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
});
