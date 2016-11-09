/**
 * Created by Jerome on 16/9/2.
 */
    var margin = {top: 20, right: 20, bottom: 30, left: 50}
//        var width = document.body.clientWidth - margin.left - margin.right
//        var height = 500 - margin.top - margin.bottom;
    var width = 720;
    var height = 340;
    var data = Array.apply(0, Array(24)).map(function(item, i) {
        // 产生31条数据
        i++;
//            de = new Date('2013-12-' + (i < 10 ? '0' + i : i))
        var de = new Date('2013-12-01')
        de.setHours(i)
        return {date: de, pv: parseInt(Math.random() * 100)}
    });

    var x = d3.time.scale()
        .domain(d3.extent(data,function (d) {
            return  d.date;
        }))
        .range([0,width]);

    var y = d3.scale.linear()
        .domain([0,d3.max(data,function (d) {
            return d.pv
        })])
        .range([height,0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient('bottom')
        .tickFormat(d3.time.format("%H:%M"))
        .ticks(12)
        .tickSize(-height);

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient('left')
        .ticks(7)
        .tickSize(-width);

    var container = d3.select('body')
        .append('svg')
        .attr('width', width + margin.left + margin.right + 20)
//            .attr('height', height + margin.top + margin.bottom);
        .attr('height', '380px');

    var svg = container.append('g')
        .attr('class', 'content')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')

    // 横坐标
    svg.append('g')
      .attr('class', 'x axis')
      .attr('transform', 'translate(0,' + height + ')')
      .call(xAxis)
      // 增加坐标值说明
      .append('text')
      .text('Time')
      .attr('transform', 'translate(' + width + ', 0)');

    // 纵坐标
    svg.append('g')
      .attr('class', 'y axis')
      .call(yAxis)
      .append('text')
      .text('People');

    var line = d3.svg.line()
            .x(function (d) {
                return x(d.date);
            })
            .y(function (d) {
                return y(d.pv);
            })
            .interpolate('monotone');
    var path = svg.append('path')
            .attr('class','line_path')
            .attr('d',line(data))

    tips = svg.append('g').attr('class', 'tips');

    tips.append('rect')
      .attr('class', 'tips-border')
      .attr('width', 200)
      .attr('height', 50)
      .attr('rx', 10)
      .attr('ry', 10);

    var wording1 = tips.append('text')
      .attr('class', 'tips-text')
      .attr('x', 10)
      .attr('y', 20)
      .text('');

    var wording2 = tips.append('text')
      .attr('class', 'tips-text')
      .attr('x', 10)
      .attr('y', 40)
      .text('');

    container
      .on('mousemove', function() {
        var m = d3.mouse(this),
          cx = m[0] - margin.left;

        var x0 = x.invert(cx);
        var i = (d3.bisector(function(d) {
          return d.date;
        }).left)(data, x0, 1);

        var d0 = data[i - 1],
          d1 = data[i] || {},
          d = x0 - d0.date > d1.date - x0 ? d1 : d0;

        function formatWording(d) {
          return 'Time：' + d3.time.format('%Y-%m-%d')(d.date);
        }
        wording1.text(formatWording(d));
        wording2.text('People：' + d.pv);

        var x1 = x(d.date),
          y1 = y(d.pv);

        // 处理超出边界的情况
        var dx = x1 > width ? x1 - width + 200 : x1 + 200 > width ? 200 : 0;

        var dy = y1 > height ? y1 - height + 50 : y1 + 50 > height ? 50 : 0;

        x1 -= dx;
        y1 -= dy;

        d3.select('.tips')
          .attr('transform', 'translate(' + x1 + ',' + y1 + ')');

        d3.select('.tips').style('display', 'block');
      })
      .on('mouseout', function() {
        d3.select('.tips').style('display', 'none');
      });
