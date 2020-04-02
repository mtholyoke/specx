var arrayColors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a'];
var modal = document.getElementById('myModal');

// When the user clicks on <span> (x), close the modal
d3.selectAll('.modalclose').on('click', function() {
  modal.style.display = "none";
});

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

$('#compareGlobal').click(function() {
  var selectedSampleList = [];
   $.ajax({
        url: '/getCompareList',
        type: 'GET',
        success: function(response) {
          selectedSampleList = response;

          d3.select('#modalSpace').selectAll('*').remove();
          var base = d3.select('#modalSpace');
          var XminOfMin = Number.POSITIVE_INFINITY, XmaxOfMax = Number.NEGATIVE_INFINITY, YminOfMin = Number.POSITIVE_INFINITY, YmaxOfMax = Number.NEGATIVE_INFINITY;
          var xThisMin, yThisMin, xThisMax, yThisMax;
          base.append('span').text('Clear All').attr('class','removeall')
          var allGraphSVG = base.append('svg').attr('height','300').attr('width','600')
                        .attr('id','allgraph');
          modal.style.display = "block";
          d3.select('.modal-content').style('float','left').style('position','absolute')
          .style('left','6%');
          plotArray = []
          for(var i=0; i < selectedSampleList.length; i++){
            var sample = selectedSampleList[i];
            var eachSample = base.append('span').attr('class','capsule').attr('d-sample',sample.sample_no);
            eachSample.append('span').text(sample.sample_name +"|"+sample.temperature+' (K)').style('color', arrayColors[i]);
            eachSample.append('a').attr('href', '/datafile/'+sample.sample_no).text('Dataset (Counts)')
              .attr('class','subsamplelink');
            eachSample.append('a').attr('href', '/textfile/'+sample.sample_no).text('Dataset (Text)')
              .attr('class','subsamplelink');
            eachSample.append('span').attr('d-sample', sample.sample_no).text('Remove')
              .attr('class','removesample');


            xThisMin = d3.min(sample.plot.map(o => o.x));
            xThisMax = d3.max(sample.plot.map(o => o.x));

            yThisMin = d3.min(sample.plot.map(o => o.y));
            yThisMax = d3.max(sample.plot.map(o => o.y));

            if(xThisMin < XminOfMin)
              XminOfMin = xThisMin

            if(yThisMin < YminOfMin)
              YminOfMin = yThisMin

            if(xThisMax > XmaxOfMax)
              XmaxOfMax = xThisMax

            if(yThisMax > YmaxOfMax)
              YmaxOfMax =  yThisMax

            plotArray.push(sample.plot);

            $('.removeall').click(function(){
               $.ajax({
                url: '/clearCompareList',
                type: 'POST',
                success: function(response) {
                  d3.select('#modalSpace').selectAll('*').remove();
                },
                error: function(error) {
                  console.log(error);
                }
              });
            });

            $('.removesample').click(function(){
              var selectedSample = $(this).attr('d-sample');
               $.ajax({
                url: '/removeFromCompare',
                data: selectedSample,
                type: 'POST',
                success: function(response) {
                  $('#compareGlobal').trigger('click');
                },
                error: function(error) {
                  console.log(error);
                }
              });
            });


          }
          loadMultiSamples(allGraphSVG, plotArray, XminOfMin, XmaxOfMax, YminOfMin, YmaxOfMax, 250, 500)

  },
    error: function(error) {
      console.log(error);
    }
  });
});




function loadMultiSamples(svg, dataArray,  XminOfMin, XmaxOfMax, YminOfMin, YmaxOfMax, height, width){
  var line, path;
  var margin = {top: 10, right: 20, bottom: 10, left: 50};
  var group = svg.append('g').attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var xScale = d3.scaleLinear()
          .domain([XminOfMin, XmaxOfMax])
          .range([0, width]).nice(10);

    var yScale = d3.scaleLinear()
          .domain([YminOfMin, YmaxOfMax])
          .range([0,height]).nice(10);

    var xAxisGroup = group.append('g');
    var yAxisGroup = group.append('g');

    var xAxis = d3.axisBottom().ticks(5).scale(xScale)
        .tickPadding(5).tickSize(-height);
    var yAxis = d3.axisLeft().ticks(5).scale(yScale)
        .tickPadding(5).tickSize(-width);

    xAxisGroup.attr("transform", "translate(0," + height + ")").call(xAxis);
    yAxisGroup.call(yAxis);

    group.append("text")
          .attr('class','axeslabel')
          .attr("text-anchor", "middle")
          .attr("transform", "translate("+ (-40) +","+(height/2)+")rotate(-90)")
          .text("% Transmission");
    group.append("text")
      .attr('class','axeslabel')
      .attr("text-anchor", "middle")
      .attr("transform", "translate("+ (width/2) +","+(height-(-25))+")")
      .text("(Velocity(mm/s))");

    dataArray.forEach((data,i) => {

    line = d3.line()
        .x(d => xScale(d.x))
        .y(d => yScale(d.y))
        .curve(d3.curveMonotoneX)

    path = group.append("path")
        .datum(data)
        .attr("class", "line")
        .style('stroke', arrayColors[i])
        .attr("d", line);

  });
}

$(".sl").each(function () {
  $(this).attr('href',' ../sample/'+encodeURIComponent($(this).text()));
});
