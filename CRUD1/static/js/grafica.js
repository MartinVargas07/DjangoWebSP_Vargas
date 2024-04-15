document.addEventListener("DOMContentLoaded", function () {
  // Obtener las opciones del gráfico desde la variable chartOptions
  var options = chartOptions;
  var labels = charLabels;
  
  // Actualizar las etiquetas en las opciones del gráfico
  options.series[0].label = {
    show: true,
    formatter: function (params) {
      var index = params.dataIndex;
      return labels[index];
    },
  };
  // Crear una instancia de gráfico utilizando las opciones
  var chart = echarts.init(document.getElementById('chart-container'));
  chart.setOption(options);
});
