import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import 'chartjs-adapter-moment';

function ChartGenerate({ chartData = {}, chartLabel, chartId }) {


    const chartRef = useRef(null);
    const chartInstance = useRef(null);

    useEffect(() => {
        // Ensure chartData is a valid dictionary
        if (typeof chartData !== 'object' || chartData === null) {
            console.error("Invalid chartData format. Expected a dictionary.");
            return;
        }

        const ctx = chartRef.current.getContext('2d');

        // Extract keys (datetime) and values from the dictionary
        const dates = Object.keys(chartData).map(key => new Date(key)); // Convert keys to Date objects
        const values = Object.values(chartData); // Extract corresponding values

        if (chartInstance.current) {
            chartInstance.current.destroy();
        }

        chartInstance.current = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: chartLabel,
                        data: values,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            parser: true,
                            tooltipFormat: 'YYYY-MM-DD',
                            unit: 'month',
                        },
                        title: {
                            display: true,
                            text: 'Date',
                        },
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Value',
                        },
                    },
                },
            },
        });

        return () => {
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, [chartData, chartLabel]);

    return (
        <canvas id={chartId} ref={chartRef} style={{ width: '100%', height: '400px' }}></canvas>
    );
}

export default ChartGenerate;
