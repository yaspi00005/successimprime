$(function(e) {

	/* Chartjs (#chart) */
	var myCanvas = document.getElementById("chart");
	myCanvas.height="296";

	var myCanvasContext = myCanvas.getContext("2d");
	var gradientStroke = myCanvasContext.createLinearGradient(0, 0, 0, 380);
	gradientStroke.addColorStop(0, 'rgba(163, 67, 255,0.2)');

	var myChart = new Chart( myCanvas, {
		type: 'line',
		data: {
			labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul","Aug"],
			datasets: [{
				label: "Incoming calls",
				backgroundColor: gradientStroke,
				borderColor: '#a343ff',
				hoverBackgroundColor: gradientStroke,
				hoverBorderWidth: 2,
				pointRadius :2,
				pointHoverRadius :2,
				borderWidth: 2,
				hoverBorderColor: 'gradientStroke1',
				data: [28, 50, 30, 58, 41, 70, 45,45, 60,80 ]
			}]
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			tooltips: {
				mode: 'index',
				titleFontSize: 12,
				titleFontColor: 'rgba(225,225,225,0.9)',
				bodyFontColor: 'rgba(225,225,225,0.9)',
				backgroundColor: 'rgba(0,0,0,0.7)',
				cornerRadius: 3,
				intersect: false,
			},
			legend: {
				display: false,
				labels: {
					usePointStyle: true,
					fontFamily: 'Montserrat',
				},
			},
			scales: {
				xAxes: [{
					ticks: {
						fontColor: "rgba(225,225,225,0.5)",
					 },
					display: true,
					gridLines: {
						display: true,
						color: 'rgba(225,225,225,0.03)',
						drawBorder: false
					},
					scaleLabel: {
						display: false,
						labelString: 'Month',
						fontColor: 'rgba(225,225,225,0.03)'
					}
				}],
				yAxes: [{
					ticks: {
						fontColor: "transparent",
					 },
					display: true,
					gridLines: {
						display: true,
						color: 'rgba(225,225,225,0.03)',
						drawBorder: false
					},
					scaleLabel: {
						display: false,
						labelString: 'sales',
						fontColor: 'rgba(225,225,225,0.5)'
					}
				}]
			},
			title: {
				display: false,
				text: 'Normal Legend'
			}
		}
	});
	/* Chartjs (#chart) closed */

	/* Chartjs (#survey) */
	var myCanvas = document.getElementById("survey");
	myCanvas.height="290";

	var myCanvasContext = myCanvas.getContext("2d");
	var gradientStroke1 = myCanvasContext.createLinearGradient(0, 0, 0, 380);
	gradientStroke1.addColorStop(0, '#a343ff');

	var gradientStroke2 = myCanvasContext.createLinearGradient(0, 0, 0, 300);
	gradientStroke2.addColorStop(0, '#00b3ff');
	var myChart = new Chart(myCanvas, {
		type: 'bar',
		data: {
			labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
			datasets: [{
				label: 'Manager Count',
				data: [15, 18, 12, 14, 10, 15, 7, 14],
				backgroundColor: gradientStroke1,
				hoverBackgroundColor: gradientStroke1,
				hoverBorderWidth: 2,
				hoverBorderColor: 'gradientStroke1'
			}, {

			    label: 'Employee Count',
				data: [10, 14, 10, 15, 9, 14, 15, 20],
				backgroundColor: gradientStroke2,
				hoverBackgroundColor: gradientStroke2,
				hoverBorderWidth: 2,
				hoverBorderColor: 'gradientStroke2'
			}
		  ]
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			tooltips: {
				mode: 'index',
				titleFontSize: 12,
				titleFontColor: 'rgba(225,225,225,0.9)',
				bodyFontColor: 'rgba(225,225,225,0.9)',
				backgroundColor: 'rgba(0,0,0,0.7)',
				cornerRadius: 3,
				intersect: false,
			},
			legend: {
				display: true,
				labels: {
					display: true,
					usePointStyle: true,
					fontColor: 'rgba(255,255,255,0.5)'
				},
			},
			scales: {
				xAxes: [{
					barPercentage: 0.5,
					ticks: {
						fontColor: "rgba(225,225,225,0.5)",

					 },
					display: true,
					gridLines: {
						display: true,
						color: 'rgba(225,225,225,0.1)',
						drawBorder: false
					},
					scaleLabel: {
						display: false,
						labelString: 'Month',
						fontColor: 'rgba(225,225,225,0.5)'
					}
				}],
				yAxes: [{
					ticks: {
						fontColor: "rgba(225,225,225,0.5)",
					 },
					display: true,
					gridLines: {
						display: true,
						color: 'rgba(225,225,225,0.1)',
						drawBorder: false
					},
					scaleLabel: {
						display: false,
						labelString: 'sales',
						fontColor: 'rgba(225,225,225,0.5)'
					}
				}]
			},
			title: {
				display: false,
				text: 'Normal Legend'
			}
		}
	});
	/* Chartjs (#survey) closed */

	/* Chartjs (#turnover-rate) */
	var ctx = document.getElementById("turnover-rate");
    var myChart = new Chart( ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul','Aug','Sep','Oct'],
            type: 'line',
            datasets: [ {
                data: [1, 7, 3, 9, 4, 5, 2, 4,1,0],
                label: 'Resolved-complaints',
                backgroundColor: 'rgb(163, 67, 255,0.2)',
                borderColor: '#a343ff',
				borderWidth: 2
            }, ]
        },
        options: {
            maintainAspectRatio: true,
            legend: {
                display: false
            },
            responsive: true,
            tooltips: {
                mode: 'index',
                titleFontSize: 12,
                titleFontColor: 'rgba(255, 255, 255, 0.5)',
				bodyFontColor: 'rgba(255, 255, 255, 0.5)',
				backgroundColor: 'rgba(0, 0, 0, 0.9)',
                cornerRadius: 0,
                intersect: false,
            },
            scales: {
                xAxes: [ {
                    gridLines: {
                        color: 'transparent',
                        zeroLineColor: 'transparent'
                    },
                    ticks: {
                        fontSize: 2,
                        fontColor: 'transparent'
                    }
                } ],
                yAxes: [ {
                    display:false,
                    ticks: {
                        display: false,
                    }
                } ]
            },
            title: {
                display: false,
            },
            elements: {
                line: {
                    borderWidth: 4
                },
                point: {
                    radius: 0,
                    hitRadius: 10,
                    hoverRadius: 2
                }
            }
        }
    });
	/* Chartjs (#turnover-rate) closed */
   
    /* Sparline bar*/
	$(".sparkline_bar1").sparkline([2, 4, 3, 4, 5, 4, 5, 0, 3, 5, 6, 4, 4, 4, 5, 3, 5], {
		type: 'bar',
		height: 77,
		width:250,
		barWidth: 4,
		barSpacing: 9,
		colorMap: {
			'9': '#a1a1a1'
		},
		barColor: '#ffbb57 '
	});
	/* Sparline bar closed*/

});


