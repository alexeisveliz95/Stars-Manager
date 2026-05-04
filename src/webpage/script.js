document.addEventListener("DOMContentLoaded", function() {
    // Función para cargar los datos del JSON
    async function loadData() {
        try {
            // Simulamos que los datos vienen de archivos JSON
            const starsData = await fetch('/data/current.json');
            const starsJSON = await starsData.json();

            // Actualizamos la UI con los datos
            document.getElementById("stars").textContent = starsJSON.stars;
            document.getElementById("forks").textContent = starsJSON.forks;
            document.getElementById("watchers").textContent = starsJSON.watchers;

            // Gráfico de crecimiento
            const growthData = await fetch('/data/history-stars.json');
            const historyJSON = await growthData.json();

            const dates = historyJSON.map(entry => entry.date);
            const stars = historyJSON.map(entry => entry.stars);

            const ctx = document.getElementById('growthChart').getContext('2d');
            const growthChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Stars en el tiempo',
                        data: stars,
                        borderColor: '#4caf50',
                        backgroundColor: 'rgba(76, 175, 80, 0.2)',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Insights automáticos (ejemplo)
            const insightsData = await fetch('/data/insights.json');
            const insightsJSON = await insightsData.json();

            document.getElementById("insightMessage").textContent = insightsJSON.message;
        } catch (error) {
            console.error("Error al cargar los datos:", error);
        }
    }

    // Llamamos la función para cargar los datos al cargar la página
    loadData();
});