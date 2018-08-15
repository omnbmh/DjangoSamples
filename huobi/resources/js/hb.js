;(function(window, undefined){
    "use strict";
    var $ = window.jQuery;
    // refresh settings
    $('#refresh-system-settings').click(function(){
        $.getJSON('/order/refresh_settings',function(data){
          alert(data.status);
      });
    });

    $('#refresh-trading-coins-settings').click(function(){
        $.getJSON('/order/init/symbol',function(data){
          alert(data.status);
      });
    });
    $('#refresh-kline-history').click(function(){
        $.getJSON('/kline/init',function(data){
          alert(data.status);
      });
    });$('#start_t_kline_history').click(function(){
        $.getJSON('/thread/kline/start',function(data){
          alert(data.status);
      });
    });
  })(window);