$(function(e) {
	
	/* chartjs (#recurring-revenue) */
	var myCanvas = document.getElementById("recurring-revenue");
	myCanvas.height="300";

	var myCanvasContext = myCanvas.getContext("2d");
	var gradientStroke1 = myCanvasContext.createLinearGradient(0, 0, 0, 360);
	gradientStroke1.addColorStop(0, 'rgba(163, 67, 255, 0.9)');

	var gradientStroke2 = myCanvasContext.createLinearGradient(0, 0, 0, 360);
	gradientStroke2.addColorStop(0, 'rgba(0, 179, 255, 0.9)');

    var myChart = new Chart( myCanvas, {
		type: 'bar',
		data: {
			labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
			datasets: [{
				label: 'Business',
				data: [15, 13, 12, 14, 10, 15, 7, 14],
				backgroundColor: gradientStroke1,
				hoverBackgroundColor: gradientStroke1,
				hoverBorderWidth: 2,
				hoverBorderColor: gradientStroke1
			},{
			label: 'Enterprise',
				data: [10, 14, 10, 15, 9, 13, 15, 18],
				backgroundColor: gradientStroke2,
				hoverBackgroundColor: gradientStroke2,
				hoverBorderWidth: 2,
				hoverBorderColor: gradientStroke2
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
				},
			},
			scales: {
				xAxes: [{
					barPercentage: 0.3,
					ticks: {
						fontColor: "rgba(255, 255, 255, 0.5)",

					 },
					display: true,
					gridLines: {
						display: false,
						drawBorder: false
					},
					scaleLabel: {
						display: false,
						labelString: 'Business',
						fontColor: 'rgba(255, 255, 255, 0.5)'
					}
				}],
				yAxes: [{
					ticks: {
						fontColor: "rgba(255, 255, 255, 0.5)",
					 },
					display: true,
					gridLines: {
						display: false,
						drawBorder: false
					},
					scaleLabel: {
						display: false,
						labelString: 'Enterprise',
						fontColor: 'rgba(255, 255, 255, 0.5)'
					}
				}]
			},
			title: {
				display: false,
				text: 'Normal Legend'
			}
		}
	});
	/* chartjs (#recurring-revenue) closed */
	
	var myCanvas = document.getElementById("recurring-investment");
	myCanvas.height="300";

	var myCanvasContext = myCanvas.getContext("2d");
	var gradientStroke1 = myCanvasContext.createLinearGradient(0, 0, 0, 360);
	gradientStroke1.addColorStop(0, 'rgba(163, 67, 255, 0.9)');

	var gradientStroke2 = myCanvasContext.createLinearGradient(0, 0, 0, 360);
	gradientStroke2.addColorStop(0, 'rgba(0, 179, 255, 0.9)');

    var myChart = new Chart( myCanvas, {
		type: 'line',
		data: {
			labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
			datasets: [{
			label: 'Enterprise',
				data: [10, 14, 10, 15, 9, 13, 15, 18],
				backgroundColor: gradientStroke2,
				hoverBackgroundColor: gradientStroke2,
				hoverBorderWidth: 2,
				hoverBorderColor: gradientStroke2
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
				},
			},
			scales: {
				xAxes: [{
					barPercentage: 0.3,
					ticks: {
						fontColor: "rgba(255, 255, 255, 0.5)",

					 },
					display: true,
					gridLines: {
						display: false,
						drawBorder: false
					},
					scaleLabel: {
						display: false,
						labelString: 'Business',
						fontColor: 'rgba(255, 255, 255, 0.5)'
					}
				}],
				yAxes: [{
					ticks: {
						fontColor: "rgba(255, 255, 255, 0.5)",
					 },
					display: true,
					gridLines: {
						display: false,
						drawBorder: false
					},
					scaleLabel: {
						display: false,
						labelString: 'Enterprise',
						fontColor: 'rgba(255, 255, 255, 0.5)'
					}
				}]
			},
			title: {
				display: false,
				text: 'Normal Legend'
			}
		}
	});
	/* chartjs (#recurring-revenue) closed */

	/* chartjs (#purchase) */
	var myCanvas = document.getElementById("purchase");
	myCanvas.height="300";

	var myCanvasContext = myCanvas.getContext("2d");
	var gradientStroke1 = myCanvasContext.createLinearGradient(0, 0, 0, 380);
	gradientStroke1.addColorStop(0, 'rgba(163, 67, 255, 0.3)');
	
	var gradientStroke2 = myCanvasContext.createLinearGradient(0, 0, 0, 280);
	gradientStroke2.addColorStop(0, 'rgb(0, 179, 255 ,0.3)');
	
    var myChart = new Chart( myCanvas, {
		type: 'line',
		data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            type: 'line',
            datasets: [ {
				label: 'view price',
				data: [16, 32, 18, 26, 42, 33, 44],
				backgroundColor: gradientStroke1,
				borderColor: '#a343ff',
				pointBackgroundColor:'#a343ff',
				pointHoverBackgroundColor:gradientStroke1,
				pointBorderColor :'#a343ff',
				pointHoverBorderColor :gradientStroke1,
				pointBorderWidth :3,
				pointRadius :3,
				pointHoverRadius :2,
				borderWidth: 2
            }, {
				label: "purchase price",
				data: [ 22, 44, 67, 43, 76, 45, 50],
				backgroundColor: gradientStroke2,
				borderColor: '#00b3ff ',
				pointBackgroundColor:'#00b3ff',
				pointHoverBackgroundColor:gradientStroke2,
				pointBorderColor :'#00b3ff ',
				pointHoverBorderColor :gradientStroke2,
				pointBorderWidth :3,
				pointRadius :3,
				pointHoverRadius :2,
				borderWidth: 2
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
					usePointStyle: false,
				},
			},
			scales: {
				xAxes: [{
					ticks: {
						fontColor: "rgba(255,255,255,0.5)",
					 },
					display: true,
					gridLines: {
						display: false,
						drawBorder: false
					},
					scaleLabel: {
						display: false,
						labelString: 'Month',
						fontColor: 'transparent'
					}
				}],
				yAxes: [{
					ticks: {
						fontColor: "rgba(255,255,255,0.5)",
					 },
					display: true,
					gridLines: {
						display: false,
						drawBorder: false
					},
					scaleLabel: {
						display: false,
						labelString: 'sales',
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
	/* chartjs (#purchase) closed */
	
    /* chartjs (#sales-status) */
    var ctx = document.getElementById("sales-status");
	var myChart = new Chart(ctx, {
		type: 'line',
		data: {
			labels: ["P1-6", "p1-8", "p2-6", "p2-8", "p3-6", "p3-8", "p4-6", "p4-8", "p5-6", "p5-8", "p6-6", "p6-8"],
			type: 'line',
			datasets: [{
				label: "Expenses",
				data: [24000, 20000, 18000, 14000, 12000, 17000, 24000, 22000, 25000, 30000, 20000, 14000],
				backgroundColor: 'transparent',
				borderColor: '#a343ff ',
				borderWidth: 3,
				pointStyle: 'circle',
				pointRadius: 0,
				pointBorderColor: 'transparent',
				pointBackgroundColor: '#a343ff',
			}, {
				label: "Budget",
				data: [14000, 22000, 25000, 20000, 24000, 14000, 16000, 18000, 26000, 28000, 16000, 12000],
				backgroundColor: 'transparent',
				borderColor: '#00b3ff',
				borderWidth: 3,
				pointStyle: 'circle',
				pointRadius: 0,
				pointBorderColor: 'transparent',
				pointBackgroundColor: '#00b3ff',
			}]
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			tooltips: {
				mode: 'index',
				titleFontSize: 12,
				titleFontColor: 'rgba(255,255,255,0.5)',
				bodyFontColor: 'rgba(255,255,255,0.5)',
				backgroundColor: 'rgba(0,0,0,0.8)',
				bodyFontFamily: 'Montserrat',
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
						color: 'rgba(255,255,255,0.1)'
					},
					scaleLabel: {
						display: false,
						labelString: ''
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
						display: false,
						labelString: 'Response time In secs'
					}
				}]
			},
			title: {
				display: false,
				text: 'Normal Legend'
			}
		}
	});
	/* chartjs (#sales-status) closed */
	
	/* echart (#active-users) */
	var chartdata = [
	{
		name: 'sales',
		type: 'bar',
		data: [120, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
		barWidth: 10,
	}
	];

	var option6 = {
		grid: {
		top: '6',
		right: '10',
		bottom: '17',
		left: '32',
	},
	xAxis: {
		type: 'value',
		axisLine: {
		lineStyle: {
		color: 'rgba(255,255,255,0.5)'
		}
	},
	splitLine: {
		lineStyle: {
		color: 'rgba(255,255,255,0.1)'
		}
	},
	axisLabel: {
		fontSize: 10,
		color: 'rgba(255,255,255,0.5)'
		}
	},

	yAxis: {
		type: 'category',
		data: ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018'],
		splitLine: {
		lineStyle: {
		color: '#fff'
		}
	},
	axisLine: {
		lineStyle: {
		color: '#eaeaea'
		}
	},
	axisLabel: {
		fontSize: 10,
		color: 'rgba(255,255,255,0.5)'
		}
	},
	series: chartdata,
		color:[ 'rgb(163, 67, 255,0.9)']
	};

	var chart6 = document.getElementById('active-users');
	var barChart6 = echarts.init(chart6);
	barChart6.setOption(option6);
	
	/* echart (#active-users) closed */
	
 });