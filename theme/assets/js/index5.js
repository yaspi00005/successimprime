(function($) {
	"use strict";

	/* Chartjs (#profit-overview) */
	var myCanvas = document.getElementById("profit-overview");
	myCanvas.height="300";

	var myCanvasContext = myCanvas.getContext("2d");
	var gradientStroke1 = myCanvasContext.createLinearGradient(0, 0, 0, 300);
	gradientStroke1.addColorStop(0, 'rgba(163, 67, 255,0.9)');
	
	var gradientStroke2 = myCanvasContext.createLinearGradient(0, 0, 0, 390);
	gradientStroke2.addColorStop(0, 'rgba(0, 179, 255,0.9)');

    var myChart = new Chart( myCanvas, {
		type: 'bar',
		data: {
			labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
			datasets: [{
				label: 'Total clicks',
				data: [15, 18, 12, 14, 10, 15, 7, 14],
				backgroundColor: gradientStroke1,
				hoverBackgroundColor: gradientStroke1,
				hoverBorderWidth: 2,
				hoverBorderColor: 'gradientStroke1'
			}, {

			    label: 'Total Impressions',
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
				titleFontColor: 'rgba(255, 255, 255, 0.5)',
				bodyFontColor: 'rgba(255, 255, 255, 0.5)',
				backgroundColor: 'rgba(0, 0, 0, 0.9)',
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
					barPercentage: 0.3,
					ticks: {
						fontColor: "rgba(255,255,255,0.5)",

					 },
					display: true,
					gridLines: {
						display: true,
						color: 'transparent',
						drawBorder: false
					},
					scaleLabel: {
						display: false,
						labelString: 'Month',
						fontColor: 'rgba(255,255,255,0.5)'
					}
				}],
				yAxes: [{
					ticks: {
						fontColor: "rgba(255,255,255,0.5)",
					 },
					display: false,
					gridLines: {
						display: true,
						color: 'rgba(255,255,255,0.03)',
						drawBorder: false
					},
					scaleLabel: {
						display: false,
						labelString: 'sales',
						fontColor: 'rgba(255,255,255,0.5)'
					}
				}]
			},
			title: {
				display: false,
				text: 'Normal Legend'
			}
		}
	});
	/* Chartjs (profit-overview) closed */

	/* Chartjs (#compaign) */
	var ctx = document.getElementById('compaign').getContext('2d');
	var gradientStroke1 = ctx.createLinearGradient(0, 0, 0, 330);
	gradientStroke1.addColorStop(0, 'rgba(163, 67, 255,0.2)');
	var myChart = new Chart(ctx, {
		type: 'line',
		data: {
			labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
			type: 'line',
			datasets: [{
				label: "Total installs %",
				data: [85, 75, 96, 84, 85, 92, 79, 78, 74, 85, 86, 80],
				backgroundColor: gradientStroke1,
				borderColor: '#30c102 ',
				borderWidth: 2,
				pointStyle: 'circle',
				pointRadius: 0,
				pointBorderColor: 'transparent',
				pointBackgroundColor: '#00d9bf',
			}]
		},
		options: {
			responsive: true,
			maintainAspectRatio: true,
			tooltips: {
                mode: 'index',
                titleFontSize: 12,
                titleFontColor: '#6b6f80',
                bodyFontColor: '#6b6f80',
                backgroundColor: '#fff',
                cornerRadius: 3,
                intersect: false,
            },
			legend: {
				display: false,
				labels: {
					usePointStyle: true,
				},
			},
			scales: {
				xAxes: [{
					ticks: {
						fontColor: "rgba(255,255,255,0.5)",
					},
					display: true,
					gridLines: {
						color: 'rgba(255,255,255,0.061)'
					},
					scaleLabel: {
						display: true,
						labelString: '',
						fontColor: 'rgba(255,255,255,0.61)'
					}
				}],
				yAxes: [{
					ticks: {
						fontColor: "rgba(255,255,255,0.5)",
					},
					display: true,
					gridLines: {
						display: false,
						drawBorder: true
					},
					scaleLabel: {
						display: true,
						labelString: 'Total installs',
						fontColor: 'rgba(255,255,255,0.61)'
					}
				}]
			},
			title: {
				display: false,
				text: 'Normal Legend'
			}
		}
	});
	/* Chartjs (#compaign) closed */
	
	/* Chartjs (#adoption) */
	var ctx = document.getElementById( "adoption" );
	ctx.height=200;
    var myChart = new Chart( ctx, {
        type: 'line',
        data : {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            type: 'line',
             datasets: [
			{
				label: "Active Users",
				backgroundColor: "rgb(163, 67, 255,0.2)",
				borderColor: '#30c102',
				data: [2,7,3,5,4,5,2,8,4,6,5,2,8,4,7,2,4,6,4,8,4]
			}, {
				label: "Contribution",
				backgroundColor: "rgb(0, 179, 255,0.2)",
				borderColor: '#fbbc60',
				data: [5,9,5,9,5,9,7,3,5,2,5,3,9,6,5,9,7,3,5,2,7,10]
			}
		  ]
        },
        options: {
            maintainAspectRatio: false,
            legend: {
                display: false
            },
            responsive: true,
            tooltips: {
                mode: 'index',
                titleFontSize: 12,
                titleFontColor: '#000',
                bodyFontColor: '#000',
                backgroundColor: '#fff',
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
                    borderWidth: 2
                },
                point: {
                    radius: 0,
                    hitRadius: 10,
                    hoverRadius: 4
                }
            }
        }
    } );
	/* Chartjs (#adoption) closed */

})(jQuery);
