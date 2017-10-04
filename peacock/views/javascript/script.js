
d3.json('/data/output.json', function (error,data) {

  function tabulate(data, columns) {
    var table = d3.select('body').append('table')
    var thead = table.append('thead')
    var	tbody = table.append('tbody');

    // append the header row
    thead.append('tr')
      .selectAll('th')
      .data(columns).enter()
      .append('th')
        .text(function (column) { return column; });

    // create a row for each object in the data
    var rows = tbody.selectAll('tr')
      .data(data)
      .enter()
      .append('tr');

    // create a cell in each row for each column
    var cells = rows.selectAll('td')
      .data(function (row) {
        return columns.map(function (column) {
          return {column: column, value: row[column]};
        });
      })
      .enter()
      .append('td')
        .text(function (d) { return d.value; });

	return table;
  }

  // render the table(s)
  tabulate(data, ['hostname', 'port', 'name',
    'ack_state', 'ack_reason', 'ack_completed_time',
    'null_state', 'null_reason', 'null_completed_time',
    'syn_state', 'syn_reason', 'syn_completed_time',
    'xmas_state', 'xmas_reason', 'xmas_completed_time'
  ]);

  // 'protocol',
});
