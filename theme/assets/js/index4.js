$(function(e) {
	'use strict';

	/* Chartjs (#bitcoin-cost) */
    var myCanvas = document.getElementById("bitcoin-cost");
	myCanvas.height="360";
	var myCanvasContext = myCanvas.getContext("2d");

	var gradientStroke1 = myCanvasContext.createLinearGradient(0, 0, 0, 240);
	gradientStroke1.addColorStop(0, 'rgb(163, 67, 255,0.9)');

	var gradientStroke2 = myCanvasContext.createLinearGradient(0, 0, 0, 280);
	gradientStroke2.addColorStop(0, 'rgb(0, 179, 255,0.9)');


    var myChart = new Chart( myCanvas, {

		type: 'line',
		data: {
			labels: ["Jan", "feb", "Mar", "Apr", "May", "Jun", "Jul"],
			type: 'line',
			datasets: [{
				label: 'Price',
				data: [0, 70, 75, 120, 94, 141, 162],
				backgroundColor: 'transparent',
				borderColor: gradientStroke1,
				pointBackgroundColor:'#fff',
				pointHoverBackgroundColor:gradientStroke1,
				pointBorderColor :gradientStroke1,
				pointHoverBorderColor :gradientStroke1,
				pointBorderWidth :0,
				pointRadius :0,
				pointHoverRadius :0,
				borderWidth: 4
			}, {
				label: "Market Cap",
				data: [0, 50, 40, 80, 40, 79, 120],
				backgroundColor: 'transparent',
				borderColor: gradientStroke2,
				pointBackgroundColor:'#fff',
				pointHoverBackgroundColor:gradientStroke2,
				pointBorderColor :gradientStroke2,
				pointHoverBorderColor :gradientStroke2,
				pointBorderWidth :0,
				pointRadius :0,
				pointHoverRadius :0,
				borderWidth: 4
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
				display: true,
				labels: {
					usePointStyle: true,
					fontColor: 'rgba(255,255,255,0.5)'
				},
			},
			scales: {
				xAxes: [{
					ticks: {
						fontColor: "rgba(255, 255, 255,0.5)",
					},
					display: true,
					gridLines: {
						color: 'rgba(255, 255, 255,0.1)'
					},
					scaleLabel: {
						display: true,
						labelString: 'Price',
						fontColor: 'rgba(255, 255, 255,0.85)'
					}
				}],
				yAxes: [{
					ticks: {
						fontColor: "rgba(255, 255, 255,0.5)",
					},
					display: true,
					gridLines: {
						display: false,
						drawBorder: true
					},
					scaleLabel: {
						display: true,
						labelString: 'Market cap',
						fontColor: 'rgba(255, 255, 255,0.85)'
					}
				}]
			},
			title: {
				display: false,
				text: 'Normal Legend'
			}
		}
	});
	/* Chartjs (#bitcoin-cost) closed */

	/* Chartjs (#areachart1) */
    var ctx = document.getElementById( "areachart1" );
	ctx.height = 160;
    var myChart = new Chart( ctx, {
        type: 'line',
        data: {
            labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
            type: 'line',
            datasets: [ {
                data: [5, 145, 26, 155, 65, 252, 252, 98, 215, 245, 62, 255],
                label: 'Market value',
                backgroundColor: 'rgb(163, 67, 255,0.2)',
				borderColor: 'rgb(163, 67, 255)',
				borderWidth: 2,
				pointStyle: 'circle',
				pointRadius: 0,
				pointBorderColor: 'transparent',
				pointBackgroundColor: '#30c102',
			}]
		},
		options: {
			responsive: true,
			maintainAspectRatio: true,
			legend: {
				display: false,
				labels: {
					usePointStyle: true,
				},
			},
			scales: {
				xAxes: [{
					ticks: {
						fontColor: "transparent",
					},
					display: false,
					gridLines: {
						color: 'transparent'
					},
					scaleLabel: {
						display: true,
						labelString: '',
						fontColor: 'transparent'
					}
				}],
				yAxes: [{
					ticks: {
						fontColor: "transparent",
					},
					display: false,
					gridLines: {
						display: false,
						drawBorder: true
					},
					scaleLabel: {
						display: true,
						labelString: 'Total installs',
						fontColor: 'transparent'
					}
				}]
			},
			title: {
				display: false,
				text: 'Normal Legend'
			}
		}
	});
	/* Chartjs (#areachart1) closed */

	/* Chartjs (#areachart2) */
   var ctx = document.getElementById( "areachart2" );
	ctx.height = 160;
    var myChart = new Chart( ctx, {
        type: 'line',
        data: {
            labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
            type: 'line',
            datasets: [ {
                data: [24, 18, 25, 21, 32, 28,30],
                label: 'Market value',
                backgroundColor: 'rgb(0, 179, 255,0.2)',
				borderColor: 'rgb(0, 179, 255)',
				borderWidth: 2,
				pointStyle: 'circle',
				pointRadius: 0,
				pointBorderColor: 'transparent',
				pointBackgroundColor: '#fbbc60',
			}]
		},
		options: {
			responsive: true,
			maintainAspectRatio: true,
			legend: {
				display: false,
				labels: {
					usePointStyle: true,
				},
			},
			scales: {
				xAxes: [{
					ticks: {
						fontColor: "transparent",
					},
					display: false,
					gridLines: {
						color: 'transparent'
					},
					scaleLabel: {
						display: true,
						labelString: '',
						fontColor: 'transparent'
					}
				}],
				yAxes: [{
					ticks: {
						fontColor: "transparent",
					},
					display: false,
					gridLines: {
						display: false,
						drawBorder: true
					},
					scaleLabel: {
						display: true,
						labelString: 'Total installs',
						fontColor: 'transparent'
					}
				}]
			},
			title: {
				display: false,
				text: 'Normal Legend'
			}
		}
	});
	/* Chartjs (#areachart2) closed */

	/* Chartjs (#areachart3) */
    var ctx = document.getElementById( "areachart3" );
	ctx.height = 160;
    var myChart = new Chart( ctx, {
        type: 'line',
        data: {
            labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
            type: 'line',
            datasets: [ {
                data: [30, 70, 30, 90, 50, 130, 100, 140],
                label: 'Market value',
                backgroundColor: 'rgb(245, 51, 79,0.2)',
                borderColor: 'rgb(245, 51, 79)',
				borderWidth: 2,
				pointStyle: 'circle',
				pointRadius: 0,
				pointBorderColor: 'transparent',
				pointBackgroundColor: 'rgb(245, 51, 79)',
			}]
		},
		options: {
			responsive: true,
			maintainAspectRatio: true,
			legend: {
				display: false,
				labels: {
					usePointStyle: true,
				},
			},
			scales: {
				xAxes: [{
					ticks: {
						fontColor: "transparent",
					},
					display: false,
					gridLines: {
						color: 'transparent'
					},
					scaleLabel: {
						display: true,
						labelString: '',
						fontColor: 'transparent'
					}
				}],
				yAxes: [{
					ticks: {
						fontColor: "transparent",
					},
					display: false,
					gridLines: {
						display: false,
						drawBorder: true
					},
					scaleLabel: {
						display: true,
						labelString: 'Total installs',
						fontColor: 'transparent'
					}
				}]
			},
			title: {
				display: false,
				text: 'Normal Legend'
			}
		}
	});

	var ctx = document.getElementById( "areachart4" );
	ctx.height = 160;
    var myChart = new Chart( ctx, {
        type: 'line',
        data: {
            labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
            type: 'line',
            datasets: [ {
                data: [20, 40, 45, 80, 40, 120, 100, 115],
                label: 'Market value',
                backgroundColor: 'rgb(38, 194, 247,0.2)',
                borderColor: 'rgb(38, 194, 247)',
				borderWidth: 2,
				pointStyle: 'circle',
				pointRadius: 0,
				pointBorderColor: 'transparent',
				pointBackgroundColor: 'rgb(38, 194, 247)',
			}]
		},
		options: {
			responsive: true,
			maintainAspectRatio: true,
			legend: {
				display: false,
				labels: {
					usePointStyle: true,
				},
			},
			scales: {
				xAxes: [{
					ticks: {
						fontColor: "transparent",
					},
					display: false,
					gridLines: {
						color: 'transparent'
					},
					scaleLabel: {
						display: true,
						labelString: '',
						fontColor: 'transparent'
					}
				}],
				yAxes: [{
					ticks: {
						fontColor: "transparent",
					},
					display: false,
					gridLines: {
						display: false,
						drawBorder: true
					},
					scaleLabel: {
						display: true,
						labelString: 'Total installs',
						fontColor: 'transparent'
					}
				}]
			},
			title: {
				display: false,
				text: 'Normal Legend'
			}
		}
	});
	/* Chartjs (#areachart1) closed */

	/*---HightChart Barchart (#Highchart)---*/
	Highcharts.chart('Highchart', {
		chart: {
			backgroundColor: 'transparent',
			zoomType: 'xy'
		},
		title: {
			text: ''
		},
		subtitle: {
			text: ''
		},
		exporting: {
			enabled: false
		},
		credits: {
			enabled: false
		},
		xAxis: [{
			gridLineColor: 'rgba(255,255,255,0.1)',
			categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
			crosshair: true,
			labels: {
				style: {
					color: '#fff',
				}
			}
		}],
		yAxis: [{ // Primary yAxis
			gridLineColor: 'rgba(255,255,255,0.1)',
			labels: {
				format: '{value}',
				style: {
					color: '#fff',
				}
			},
			title: {
				text: 'Last Price',
				style: {
					color: '#fff',
				}
			}
		}, { // Secondary yAxis
			gridLineColor: 'rgba(0,0,0,0.1)',
			title: {
				text: 'Daily change',
				style: {
					color: Highcharts.getOptions().colors[0]
				}
			},
			labels: {
				format: '{value} ',
				style: {
					color: Highcharts.getOptions().colors[0]
				}
			},
			opposite: true
		}],
		tooltip: {
			shared: true
		},
		legend: {
			layout: 'vertical',
			align: 'left',
			x: 120,
			verticalAlign: 'top',
			y: 100,
			floating: true,
			backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || 'rgba(0,0,0)'
		},
		series: [{
			name: 'Last Price',
			type: 'column',
			yAxis: 1,
			data: [49.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
			color: 'rgb(163, 67, 255,0.5)',
			tooltip: {
				valueSuffix: ' BTC'
			}
		}, {
			name: 'Daily Change',
			type: 'spline',
			data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6],
			color: 'rgb(0, 179, 255)',
			tooltip: {
				valueSuffix: 'BTC'
			}
		}]
	});
	/*---HightChart Barchart (#Highchart) closed---*/

});