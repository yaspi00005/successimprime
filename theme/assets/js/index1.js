$(function () {

	/* Chartjs (#expense) */
	var myCanvas = document.getElementById("expense");
	myCanvas.height="250";

	var myCanvasContext = myCanvas.getContext("2d");
	var gradientStroke1 = myCanvasContext.createLinearGradient(0, 0, 0, 230);
	gradientStroke1.addColorStop(0, 'rgb(163, 67, 255)');

	var myChart = new Chart(myCanvas, {
		type: 'bar',
		data: {
			labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun" ,"Aug", "Sep"],
			datasets: [{
				label: 'Expenses',
				data: [16, 14, 12, 14, 16, 15, 12, 14,18,10],
				backgroundColor: gradientStroke1,
				hoverBackgroundColor: gradientStroke1,
				hoverBorderWidth: 2,
				hoverBorderColor: 'gradientStroke1'
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
				display: false,
				labels: {
					usePointStyle: true,
				},
			},
			scales: {
				xAxes: [{
					 barPercentage: 0.3,
					ticks: {
						fontColor: "rgba(225,225,225,0.5)",

					 },
					display: true,
					gridLines: {
						display: false,
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
						fontColor: "transparent",
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
	/* Chartjs (#expense) closed */

	/* Chartjs (#total-budget) */
	var myCanvas = document.getElementById("total-budget");
	myCanvas.height="180";
	var myCanvasContext = myCanvas.getContext("2d");
	var gradientStroke1 = myCanvasContext.createLinearGradient(0, 0, 0, 200);

	gradientStroke1.addColorStop(0, 'rgb(0, 179, 255, 0.2)');
    var myChart = new Chart( myCanvas, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            type: 'line',
            datasets: [ {
				label: 'Market value',
				data: [30, 70, 30, 100, 50, 130, 100, 140],
				backgroundColor: gradientStroke1,
				borderColor: 'rgb(0, 179, 255) ',
				pointBackgroundColor:'#fff',
				pointHoverBackgroundColor:gradientStroke1,
				pointBorderColor :gradientStroke1,
				pointHoverBorderColor :gradientStroke1,
				pointBorderWidth :0,
				pointRadius :0,
				pointHoverRadius :0,
				borderWidth: 2
            }, ]
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
                titleFontColor: 'rgba(225,225,225,0.9)',
				bodyFontColor: 'rgba(225,225,225,0.9)',
				backgroundColor: 'rgba(0,0,0,0.7)',
                cornerRadius: 3,
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
                    borderWidth: 1
                },
                point: {
                    radius: 4,
                    hitRadius: 10,
                    hoverRadius: 4
                }
            }
        }
    });
	/* Chartjs (#total-budget) closed */

	/* Chart-js (#budget) */
	var myCanvas = document.getElementById("budget");
	myCanvas.height="290";
	var myCanvasContext = myCanvas.getContext("2d");
	var gradientStroke1 = myCanvasContext.createLinearGradient(0, 0, 0, 200);
	gradientStroke1.addColorStop(0, 'rgb(163, 67, 255,0.2)');

	var gradientStroke2 = myCanvasContext.createLinearGradient(0, 0, 0, 190);
	gradientStroke2.addColorStop(0, 'rgb(0, 179, 255,0.2)');
	var myChart = new Chart( myCanvas, {
		type: 'line',
		data : {
			labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
			type: 'line',
			 datasets: [
			{
				label: "Expenses",
				data: [5,2,8,4,7,2,4,6,4,8,4,2,7,3,5,4,5,2,8,4,6,],
				backgroundColor: gradientStroke1,
				borderColor: 'rgb(163, 67, 255)' ,
				pointBackgroundColor:'#fff',
				pointHoverBackgroundColor:gradientStroke1,
				pointBorderColor :gradientStroke1,
				pointHoverBorderColor :gradientStroke1,
				pointBorderWidth :0,
				pointRadius :0,
				pointHoverRadius :0,
				labelColor:gradientStroke1,
				borderWidth: 2,

			}, {
				label: "Budget",
				data: [2,5,3,9,6,5,9,7,3,5,2,7,10,5,9,5,9,5,9,7,3,5],
				backgroundColor: gradientStroke2,
				borderColor: ' rgb(0, 179, 255)',
				pointBackgroundColor:'#fff',
				pointHoverBackgroundColor:gradientStroke2,
				pointBorderColor :gradientStroke2,
				pointHoverBorderColor :gradientStroke2,
				pointBorderWidth :0,
				pointRadius :0,
				pointHoverRadius :0,
				borderWidth: 2,

			}
		  ]
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			legend: {
			    labels: {
					fontColor: 'rgba(255,255,255,0.5)'
			    }
			},
			tooltips: {
				show: true,
				showContent: true,
				alwaysShowContent: true,
				triggerOn: 'mousemove',
				trigger: 'axis',
				axisPointer:
				{
					label: {
						show: false,
						color: 'rgba(255,255,255,0.1)',
					},
				}
			},

			scales: {
				xAxes: [ {
					gridLines: {
						color: 'rgba(255,255,255,0.1)',
						zeroLineColor: 'rgba(255,255,255,0.5)'
					},
					ticks: {
						fontSize: 12,
						fontColor: 'rgba(255,255,255,0.5)',
						beginAtZero: true,
						padding: 0
					}
				} ],
				yAxes: [ {
					gridLines: {
						color: 'transparent',
						zeroLineColor: 'rgba(255,255,255,0.5)'
					},
					ticks: {
						fontSize: 12,
						fontColor: 'rgba(255,255,255,0.5)',
						beginAtZero: false,
						padding: 0
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
	})
	/* Chart-js (#budget) closed */

	/* Donutchart */
	Highcharts.setOptions({
			colors: ['rgb(163, 67, 255 ,0.9)', 'rgb(255, 235, 59, 0.9)', 'rgb(249, 90, 90, 0.9)', 'rgb(0, 179, 255,0.9)','rgb(48, 193, 2, 0.9)']
	})
	Highcharts.getOptions().colors = Highcharts.map(Highcharts.getOptions().colors, function(color) {
			return {
					radialGradient: {
							cx: 0.5,
							cy: 0.5,
							r: 0.9
					},
					stops: [
							[0, color],
							[0.4, Highcharts.Color(color).brighten(-.4).get('rgb')], // darken
							[0.6, color],
							[1, Highcharts.Color(color).brighten(-.4).get('rgb')], // darken
					]
			};
	});
	var chart = new Highcharts.Chart({
		chart: {
				renderTo: 'donut',
				type: 'pie',
				backgroundColor: 'transparent',
		},
		credits: false,
		exporting: false,
		tooltip: {
				formatter: function() {
						return '<p>' + this.series.name + '<br>$' + this.point.y + '</p>';
				},
				borderRadius: 5,
				borderWidth: 2,
				backgroundColor: 'rgba(0,0,0,0.2)',
				padding: 3
		},
		plotOptions: {
				pie: {
						borderWidth: .5,
						innerSize: '70%',
						cursor: 'pointer',
						slicedOffset: 5,
						slicedOffset: 5,

						borderColor: "rgba(255,255,255,.5)",

						dataLabels: {
								enabled: false
						}
				},

				// slice animation formatter function
				series: {
						allowPointSelect: false,
						stickyTracking: false,
						point: {
								events: {
										mouseOver: function() {
												var point = this,
												points = this.series.points;


												// unslice sliced element(s)
												for (var key in points) {
														if (points[key].sliced) {
																points[key].slice(false);
														}
												}

												// slice hovered element
												if (!point.selected) {
														point.slice(true);
												}
										}
								}
						},
						events: {
								mouseOut: function(event) {
										// unslice sliced element(s)
										for (var key in this.points) {
												if (this.points[key].sliced) {
														this.points[key].slice(false);
												}
										}
								}
						}
				}
		},
		title: {
				text: false
		},

		series: [{
				data: [
						['Rent and Utilities', 44.2],
						['Travel', 26.6],
						['Marketing', 30],
						['Freelancers', 20],
						['Equipment', 22]
				],
		}, ]
	},
	// using
	function(chart) { // on complete
			var xpos = '50%';
			var ypos = '50%';
			var circleradius = 102;
			// Render the circle
			chart.renderer.circle(xpos, ypos, circleradius).attr({
					fill: 'transparent',
			}).add();
	});
   /* Donutchart closed*/

   /* Hight chart*/
    var chart = Highcharts.chart('refferal', {
	chart: {
			backgroundColor: 'transparent',
			color: '#Fff',
        },
    title: {
        text: ''
    },
	exporting: { enabled: false },
		credits: {
			enabled: false
		},
		yAxis: {
			labels: {
				style: {
					color: 'rgb(215, 231, 255,0.5)',
				}
			},
			gridLineColor: ' rgb(215, 231, 255,0.1)'
		},
		xAxis: {
			categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
			labels: {
					style: {
						color: 'rgb(215, 231, 255,0.5)',
					}
				},
		},
		colors: ['rgb(163, 67, 255 ,0.9)', 'rgb(255, 235, 59, 0.9)', 'rgb(249, 90, 90, 0.9)', 'rgb(0, 179, 255,0.9)','rgb(48, 193, 2, 0.9)','rgb(163, 67, 255 ,0.9)', 'rgb(255, 235, 59, 0.9)', 'rgb(249, 90, 90, 0.9)', 'rgb(0, 179, 255,0.9)','rgb(48, 193, 2, 0.9)'],
		series: [{
			type: 'column',
			colorByPoint: true,
			data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
			showInLegend: false
		}]

	});
	 /* Hight chart closed*/

});





