window.onload = () => {
    fetch ("/commonAffectedUsers", {
        method: 'GET',
        headers: {'Content-Type': 'application/json'}
        })
    .then(x => x.json()).then(responseData => {
        document.getElementById("totalUserCount").innerText = responseData.total_count;
        const ctx = document.getElementById('pieCountChart');
          new Chart(ctx, {
            type: 'pie',
            data: {
              labels: ['hospitalized both times', 'never hospitalized', 'hospitalized in 2022', 'hospitalized in 2021'],
              datasets: [{
                label: 'Number of Records',
                data: [responseData.hospitalized_both_years, responseData.never_hospitalized, responseData.hospitalized_in_2022, responseData.hospitalized_in_2021],
                backgroundColor: ['rgba(255, 99, 132,1)',
                'rgba(54, 162, 235,1)',
                'rgba(255, 205, 86,1)','rgb(168,50,50,1)'],hoverOffset: 5,hoverBorderWidth:2,
                borderColor: 'rgb(255, 250, 250)'}]
              
            },
            options: {
              cutout: '5%',
              animation: {
                animateRotate: true,
                animateScale: true,
              },
              responsive: false,
           }
          });
    });
    getMonthWiseUserRecoveryCount(2022, 14);
    getHospitalizationData('2022');
    getStateData('2022');
};

var barChart;

function getMonthWiseUserRecoveryCount(year, days){
    var withinDays;
    if (!days){
        withinDays = 14;
    }else{
        withinDays = days;
        document.getElementById("withinDaysCount").innerText = days;
    }
    fetch("/userRecoveryCount?forYear=" + year + "&withinDays=" + withinDays, {
        method: 'GET',
        headers: {'Content-Type': 'application/json'}
        }).then(x => x.json()).then(responseData => {
            const ctx = document.getElementById('lineCountChart');
            if(barChart){
                barChart.destroy();
            }
            barChart = new Chart(ctx, {
            type: 'bar',
            data: {
              labels: months,
              datasets: [{
                label: 'Number of Records',
                data: [
                    responseData.January,
                    responseData.February,
                    responseData.March,
                    responseData.April,
                    responseData.May,
                    responseData.June,
                    responseData.July,
                    responseData.August,
                    responseData.September,
                    responseData.October,
                    responseData.November,
                    responseData.December,
                ],
                backgroundColor: [
                  'rgba(255, 99, 132, 0.3)',
                  'rgba(255, 159, 64, 0.3)',
                  'rgba(255, 205, 86, 0.3)',
                  'rgba(255, 99, 71, 0.3)',
                  'rgba(75, 192, 192, 0.3)',
                  'rgba(54, 162, 235, 0.3)',
                  'rgba(153, 102, 255, 0.3)',
                  'rgba(23, 120, 150, 0.3)',
                  'rgba(121, 58, 72, 0.3)',
                  'rgba(26, 167, 55, 0.3)',
                  'rgba(107, 117, 68, 0.3)',
                  'rgba(210, 148, 28, 0.3)' 
                ],
                borderColor: [
                  'rgb(104, 103, 156)',
                  'rgb(104, 103, 156)',
                  'rgb(104, 103, 156)',
                  'rgb(104, 103, 156)',
                  'rgb(104, 103, 156)',
                  'rgb(104, 103, 156)',
                  'rgb(104, 103, 156)',
                  'rgb(104, 103, 156)',
                  'rgb(104, 103, 156)',
                  'rgb(104, 103, 156)',
                  'rgb(104, 103, 156)',
                  'rgb(104, 103, 156)'
                ],
                borderWidth: 3
              }]
            },
            options: {
              responsive: true,
              scales: {
                x: {
                  beginAtZero: true,
                  grid: {
                    display: false
                  }
                },
                y: {
                  beginAtZero: true,
                  grid:{
                    display:false
                  }
                }
              },
            }
          })
        });
};

function getHospitalizationData(year){
    fetch ("/monthWiseHospitalizationCount?forYear=" + year, {
        method: 'GET',
        headers: {'Content-Type': 'application/json'}
        })
    .then(x => x.json()).then(data => {
        
        renderHospitalizationChart(data);
    });
}

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

var barschart;

function renderHospitalizationChart(data){
  hosp_month_map = {
    January: {'Yes': 0, 'No': 0},
    February: {'Yes': 0, 'No': 0},
    March: {'Yes': 0, 'No': 0},
    April: {'Yes': 0, 'No': 0},
    May: {'Yes': 0, 'No': 0},
    June: {'Yes': 0, 'No': 0},
    July: {'Yes': 0, 'No': 0},
    August: {'Yes': 0, 'No': 0},
    September: {'Yes': 0, 'No': 0},
    October: {'Yes': 0, 'No': 0},
    November: {'Yes': 0, 'No': 0},
    December: {'Yes': 0, 'No': 0},
  }
  for (month in data){
    for (attr in data[month]){
        hosp_month_map[month][attr] = data[month][attr]
    }
  }
  
  var hospitalized = [];
  var not_hospitalized = [];
  for(var i=0; i<12; i++){
    hospitalized[i] = hosp_month_map[months[i]]['Yes']
    not_hospitalized[i] = hosp_month_map[months[i]]['No']
  }
  const ctx = document.getElementById('myHospitalizationChart');
  if (barschart){
    barschart.destroy();
  }
  barschart = new Chart(ctx, {
    type: 'bar',
    //type:'doughnut',
    //type:'line',
    data: {
      labels:months,
      datasets: [{
        label: 'Number of Hospitalized people',
        data: hospitalized,
        backgroundColor: [
          'rgb(255, 99, 132)'
          ],
        borderWidth: 2
      },
      {
        label: 'Number of people not hospitalized',
        data: not_hospitalized,
        backgroundColor: ['rgb(54, 162, 235)',],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      scales: {
        x: {
          beginAtZero: true,
          grid: {
            display: false
          }
        },
        y: {
          beginAtZero: true,
          grid:{
            display:false
          }
        }
      },
    }
  });
}

function getStateData(year){
    fetch ("/stateWiseAffectedUsers?forYear=" + year, {
        method: 'GET',
        headers: {'Content-Type': 'application/json'}
        })
    .then(x => x.json()).then(data => {
        
        renderStateChart(data);
    });
}

var stateChart;

states_list = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']

function renderStateChart(data){
  state_labels = []
  state_data = []
  count=0;
  for (index in data){
      for(c in states_list){
        if(states_list[c] == data[index].state){
            state_data[count] = data[index].count;
            count++;
        }
      }
  }
  const ctx = document.getElementById('myStateChart');
  if (stateChart){
    stateChart.destroy();
  }
  stateChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: states_list,
      datasets: [{
        axis: 'x',
        label: 'Number of people Affected',
        data: state_data,
        backgroundColor: ['rgba(118, 245, 239, 0.3)'],
        borderColor:['rgb(5,5,5)'],
        barThickness: 20,
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
          scales: {
            x: {
              beginAtZero: true,
              grid: {
                display: false
              },
              ticks: {
                maxRotation: 90,
                minRotation: 90
            }
            },
            y: {
              beginAtZero: true,
              grid:{
                display:false
              },
             
            }
          },
      
    }
  });
}
