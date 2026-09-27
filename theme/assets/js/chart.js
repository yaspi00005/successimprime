var color = Chart.helpers.color;
	function createConfig(legendPosition, colorName) {
		return {
			type: 'line',
			data: {
				labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
				datasets: [{
					label: 'My First dataset',
					data: [
						randomScalingFactor(),
						randomScalingFactor(),
						randomScalingFactor(),
						randomScalingFactor(),
						randomScalingFactor(),
						randomScalingFactor(),
						randomScalingFactor()
					],
					backgroundColor: color(window.chartColors[colorName]).alpha(0.5).rgbString(),
					borderColor: window.chartColors[colorName],
					borderWidth: 1
				}]
			},
			
			options: {
				responsive: true,
				maintainAspectRatio: false,
				legend: {
					position: 'bottom',
					labels: {
						fontColor: "white",
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
				
			}
		};
	}

	window.onload = function() {
		[{
			id: 'chart-legend-top',
			legendPosition: 'top',
			color: 'purple'
		}, {
			id: 'chart-legend-right',
			legendPosition: 'right',
			color: 'orange'
		}, {
			id: 'chart-legend-bottom',
			legendPosition: 'bottom',
			color: 'green'
		}, {
			id: 'chart-legend-left',
			legendPosition: 'left',
			color: 'yellow'
		}].forEach(function(details) {
			var ctx = document.getElementById(details.id).getContext('2d');
			var config = createConfig(details.legendPosition, details.color);
			new Chart(ctx, config);
			ctx.shadowColor = '';
			ctx.shadowBlur = 10;
			ctx.shadowOffsetX = 8;
			ctx.shadowOffsetY = 8;
		});
	};