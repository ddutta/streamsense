(function() {

  var slider;
  var originalTable;
  var reducedTable;

  $(document).ready(function() {
    var slider = $(".slider").slider({
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
        //alert('Changed to' + ui.value);
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
        "scrollX":        true,
        "scrollY":        "200px",
        "dom": "frtiS",
        "deferRender":    true
      });

        var reducedTable = $('#example1').DataTable( {
        "ajax": "_logcluster.output.json",
        "columns": [
          { "data": "message" },
          { "data": "@version" },
          { "data": "@timestamp" },
          { "data": "host" },
          { "data": "path" },
          { "data": "clusterid" }
          ],
        "scrollX":        true,
        "scrollY":        "200px",
        "order": [[ 5, "asc" ]],
        "dom": "frtiS",
        "deferRender":    true,
        "createdRow": function ( row, data, index ) {
            var a = (parseInt(data.clusterid))%3;
            if ( a == 0 ) {
               $(row).addClass('important');
            }
            else if (a == 1) {
               $(row).addClass('maybeimportant');
            }
            else{
               $(row).addClass('notimportant');
            }

        }
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
        "ajax": "_logcluster_serverside.output.json",
        "columns": [
          { "data": "message" },
          { "data": "@version" },
          { "data": "@timestamp" },
          { "data": "host" },
          { "data": "path" },
          { "data": "clusterid" }
          ],
          dom: "frtiS",
          scrollY: 200,
          scroller: {
            loadingIndicator: false
          },
          "order": [[ 5, "asc" ]],
          "deferRender":    true,
          "createdRow": function ( row, data, index ) {
            var a = (parseInt(data.clusterid))%3;
            if ( a == 0 ) {
               $(row).addClass('important');
            }
            else if (a == 1) {
               $(row).addClass('maybeimportant');
            }
            else{
               $(row).addClass('notimportant');
            }

        }
      });

  });

}).call(this);

