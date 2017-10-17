//scale factor
var s = 2;

//Width and height
var w = 500*s;
var h = 250*s;

//Define map projection
var projection = d3.geo.albersUsa()
                       .translate([w/2, h/2])
                       .scale([500*s]);

//Define path generator
var path = d3.geo.path()
                 .projection(projection);
                 
//Define quantize scale to sort data values into buckets of color
var color = d3.scale.quantize()
                    // .range(["rgb(237,248,233)","rgb(186,228,179)","rgb(116,196,118)","rgb(49,163,84)","rgb(0,109,44)"]);
                    .range(["#f2f0f7","#cbc9e2","#9e9ac8","#756bb1","#54278f"]);
                    //Colors taken from colorbrewer.js, included in the D3 download

//Create SVG element
var svg = d3.select("#myMap")
            .append("svg")
            .attr("width", w)
            .attr("height", h);

// Define the div for the tooltip
var tt = d3.select("#myMap").append("g") 
    .attr("class", "tooltip")       
    .style("opacity", 0);

// var stateData = 'static/data/stateData.json';
// console.log(stateData);
// console.log(JSON.parse(stateData));
// var stateData = '{{ sd|tojson }}';
// console.log("hi");
d3.json("/getMyJson", function(error, jsonData){
  // console.log(jsonData);
  color.domain(
    d3.extent(jsonData, function(d){return d.properties.rate;}))


    //Bind data and create one path per GeoJSON feature
    var paths = svg.selectAll("path")
       .data(jsonData)
       .enter()
       .append("path")
       .attr("d", path)
       .style("fill", function(d) {
            //Get data value
            var value = d.properties.rate;
            if (value) {
                return color(value);
            } else {
                return "#ccc";
            }
       })
        .on("mouseover", function(d) {    
            tt.transition()    
                .duration(200)    
                .style("opacity", .9);    
            tt.html(d.properties.name+"<br/>"
              +d.properties.num+" / "+d.properties.den+"<br/>= "
              +(d.properties.rate*100).toFixed(2)+"%") 
                .style("left", (d3.event.pageX) + "px")   
                .style("top", (d3.event.pageY - 28) + "px");  
            })          
        .on("mouseout", function(d) {   
            tt.transition()    
                .duration(500)    
                .style("opacity", 0); 
        });
       ;

});

//Create SVG element
var svg2 = d3.select("#countyMap")
            .append("svg")
            .attr("width", w)
            .attr("height", h);

// Define the div for the tooltip
var tt2 = d3.select("#countyMap").append("g") 
    .attr("class", "tooltip")       
    .style("opacity", 0);

// var stateData = 'static/data/stateData.json';
// console.log(stateData);
// console.log(JSON.parse(stateData));
// var stateData = '{{ sd|tojson }}';
// console.log("hi");
var countyData = 'static/data/counties.json';

d3.json('/countyJson', function(error, jsonData){
  console.log(jsonData['features']);
  color.domain(
    d3.extent(jsonData['features'], function(d){return d.properties.rate;}))


    //Bind data and create one path per GeoJSON feature
    var paths = svg2.selectAll("path")
       .data(jsonData['features'])
       .enter()
       .append("path")
       .attr("d", path)
       // .style("fill", "black")
       .style("fill", function(d) {
            //Get data value
            var value = d.properties.rate;
            if (value) {
                return color(value);
            } else {
                return "#ccc";
            }
       })
        .on("mouseover", function(d) {    
            tt2.transition()    
                .duration(200)    
                .style("opacity", .9);    
            tt2.html(d.properties.countyName+" "+d.properties.stateName+"<br/>"
              +d.properties.num+" / "+d.properties.den+"<br/>= "
              +(d.properties.rate*100).toFixed(2)+"%") 
                .style("left", (d3.event.pageX) + "px")   
                .style("top", (d3.event.pageY - 28) + "px");  
            })          
        .on("mouseout", function(d) {   
            tt2.transition()    
                .duration(500)    
                .style("opacity", 0); 
        });
       ;

});
