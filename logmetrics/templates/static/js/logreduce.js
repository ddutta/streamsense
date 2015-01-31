
(function() {

  var slider;
  var originalTable;
  var reducedTable;

  $(document).ready(function() {
    var slider = $(".slider" ).slider({
      range:false,
      min: 0,
      max: 64,
      value: 14,
      slide: function(e, ui) {
        var point = ui.value;
        $("#selected_value").html(point);
        var width = point;
        $("#range").css({ "width": point + "%" });
      },
      change: function(e,ui){
        $.ajax({
            type: "POST",
            url: "_slider",
            data: "value="+ui.value,
            success: function(html){
                var table = $("#example1").DataTable();
                table.clear().draw();
                table.ajax.reload();
            }
        });
      }
    });
/*
    var orginalTable = $('#example').DataTable( {
        "ajax": "_input.json",
        "columns": [
          { "data": "message" },
          { "data": "@version" },
          { "data": "@timestamp" },
          { "data": "host" },
          { "data": "path" }
          ],
        "scrollY":        "200px",
        "dom": "frtiS",
        "deferRender":    true
      });
    var reducedTable = $('#example1').DataTable( {
        "ajax": "_logreduce.output.json",
        "columns": [
          { "data": "message" },
          { "data": "@version" },
          { "data": "@timestamp" },
          { "data": "host" },
          { "data": "path" }
          ],
        "scrollY":        "200px",
        "dom": "frtiS",
        "deferRender":    true
      });
*/


    var orginalTable = $('#example').DataTable( {
        serverSide: true,
        "ajax": "_input_serverside.json",
        "columns": [
          { "data": "message" },
          { "data": "@version" },
          { "data": "@timestamp" },
          { "data": "host" },
          { "data": "path" }
          ],
        dom: "frtiS",
        scrollY: 200,
        scroller: {
            loadingIndicator: false
        }
      });
    var reducedTable = $('#example1').DataTable( {
        serverSide: true,
        "ajax": "_logreduce_serverside.output.json",
        "columns": [
          { "data": "message" },
          { "data": "@version" },
          { "data": "@timestamp" },
          { "data": "host" },
          { "data": "path" }
          ],
        dom: "frtiS",
        scrollY: 200,
        scroller: {
            loadingIndicator: false
        }
      });


  });



}).call(this);

