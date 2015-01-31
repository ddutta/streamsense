
(function() {

  var slider;
  var originalTable;
  var reducedTable;
  $(document).ready(function() {

     var datasets = [];

        $.ajax({
            type: "GET",
            url: "anomaly",
            dataType: "json",
            success: function(series){
               datasets = series;
               var j = 0;
               $.each(datasets, function(key, val) {
                  ++j;
               });

              var j=0;
              var labelgroup ="abc"
              $.each(datasets, function(key, val) {
                    if (val.label>=1)
                    {
                    var anomalyindicator = val.label;
                    val.color = j;
                    val.label = j+1;
                    if (anomalyindicator == 1)
                    {
                      if (j>0)
                      {
                         choiceContainer.append('<br><input type="radio" name="' + labelgroup +'" id="' + key + '">' +
                               '<label for="id' + key + '">' + key + "   (id="+val.label+')</label>');
                      } else {
                         choiceContainer.append('<br/><input type="radio" name="' + labelgroup + '" checked id="' + key + '">' +
                               '<label for="id' + key + '">' + key + "   (id="+val.label+')</label>');
                      }
                    }
                    else
                    {
                      if (j>0)
                      {
                         choiceContainer.append('<br><input type="radio" name="' + labelgroup +'" id="' + key + '">' +
                               '<label for="id' + key + '" style="color:#FF0000">' + key + "   (id="+val.label+')</label>');
                      } else {
                         choiceContainer.append('<br/><input type="radio" name="' + labelgroup + '" checked id="' + key + '">' +
                               '<label for="id' + key + '" style="color:#FF0000">' + key + "   (id="+val.label+')</label>');
                      }

                    }

                    j = j+1;
                    }
               });

               choiceContainer.find("input").click(plotAccordingToChoices);

               plotAccordingToChoices();
            }
        });


    var choiceContainer = $("#choices");



    function plotAccordingToChoices() {
        var data = [];

        choiceContainer.find("input:checked").each(function () {
            var key = $(this).attr("id");
            if (key && datasets[key])
                data.push(datasets[key]);
            var key2 = key + ":anomaly";
            if (key2 && datasets[key2])
               data.push(datasets[key2]);
        });

        if (data.length > 0)
            $.plot($("#placeholder"), data, {
                xaxis: { mode: "time",
                 timeformat: "%Y/%m/%d %H:%M:%S"}
            });
    }



  });

}).call(this);

