;(function(window, undefined){
    "use strict";
    var $ = window.jQuery;
    // refresh settings
    $('#refresh-settings').click(function(){
        $.getJSON('/order/refresh_settings',function(data){
          alert(data.status);
      });
    });
  })(window);