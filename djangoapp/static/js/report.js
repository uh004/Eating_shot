(function () {
    let chartInstance = null;

    function initializeChart(data) {
        const ctx = document.getElementById('canvas');

        if (chartInstance) {
            chartInstance.destroy();
        }

        const config = {
            type: 'line',
            data: data,
            options: {
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        // labels: {
                        //     fontColor: "black",
                        //     fontSize: 18,
                        //     fontFamily: 'pretendard'
                        // }
                        display: false
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: 'rgba(12, 13, 13, 1)',
                            fontSize: 16
                        },
                        grid: {
                            color: "white",
                            lineWidth: 0
                        }
                    },
                    y: {
                        min: 0,
                        max: 200,
                        ticks: {
                            fontSize: 14
                        },
                        grid: {
                            color: "white",
                            lineWidth: 0
                        }
                    }
                }
            }
        };
        console.log(config);

        chartInstance = new Chart(ctx, config);
    }

    function fetchChartData(chartType, detailType) {
        fetch(`/get_chart_data/${chartType}/${detailType}`)
            .then(response => response.json())
            .then(data => {
                initializeChart(data);
            })
            .catch(error => console.error('Error fetching chart data:', error));
    }

    function showButton() {
        const selectedOption = document.getElementById('options').value;
        const blood1Check = document.getElementById('blood1_check');
        const blood2Check = document.getElementById('blood2_check');

        // Hide both elements initially
        if (blood1Check) blood1Check.style.display = "none";
        if (blood2Check) blood2Check.style.display = "none";

        // Show the relevant element based on the selected option
        if (selectedOption === 'option1' && blood1Check) {
            blood1Check.style.display = "block";
        } else if (selectedOption === 'option2' && blood2Check) {
            blood2Check.style.display = "block";
        }

        // Fetch chart data based on the selected option and detail type
        if (selectedOption === 'option3') {
            fetchChartData(selectedOption, 'default');
        }
    }

    document.getElementById('blood1_check').addEventListener('change', function () {
        const selectedOption = document.getElementById('options').value;
        const detailType = this.value;
        console.log(detailType);
        fetchChartData(selectedOption, detailType);
    });

    document.getElementById('blood2_check').addEventListener('change', function () {
        const selectedOption = document.getElementById('options').value;
        const detailType = this.value;
        console.log(detailType);
        fetchChartData(selectedOption, detailType);
    });

    const defaultOption = document.getElementById('options').value;
    const defaultDetailType = document.getElementById('blood1_check').value;
    fetchChartData(defaultOption, defaultDetailType);

    // Expose functions to the global scope
    window.showButton = showButton;
})();


