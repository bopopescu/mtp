(function( $, window, undefined ) {
  $.danidemo = $.extend( {}, {
    
    addLog: function(id, status, str){
      var d = new Date();
      var li = $('<li />', {'class': 'demo-' + status});
       
      var message = '[' + d.getHours() + ':' + d.getMinutes() + ':' + d.getSeconds() + '] ';
      
      message += str;
     
      li.html(message);
      
      $(id).prepend(li);
    },
    
    showDetail:function(id,packageName,activity,version){
    	var template='<div class="panel panel-default">'+
				    	'<div class="panel-heading" style="text-align:left">'+packageName+
				    	'<a role="button" onclick=uninstall("'+packageName+'") style="float:right"><span class="glyphicon glyphicon-trash" aria-hidden="true" ></span> Uninstall</a>'+
				    	'</div>'+
				    	'<table class="table mytable">'+
				    		'<tbody><tr>'+
				    		'<td><span>Package</span></td><td><input style="width:100%" value="'+packageName+'"></td></tr>'+
				    		'<tr><td><span>Version</span></td><td><input style="width:100%" value="'+version+'"></td></tr>'+
				    		'<tr><td><span>Activity</span></td><td><input style="width:100%" value="'+activity+'"></td></tr></tbody>'+
				    		'</table>'+
			    		'</div>'
		$(id).prepend(template);
    },
    addFile: function(id, i, file){
    	$(id).empty()
		var template = '<div id="demo-file' + i + '">' +
		                   '<span class="demo-file-id">#' + i + '</span> - ' + file.name + ' <span class="demo-file-size">(' + $.danidemo.humanizeSize(file.size) + ')</span> - Status: <span class="demo-file-status">Waiting to upload</span>'+
		                   '<div class="progress progress-striped active" style="height:10px">'+
		                       '<div class="progress-bar" role="progressbar" style="width: 0%;">'+
		                           '<span class="sr-only">0% Complete</span>'+
		                       '</div>'+
		                   '</div>'+
		               '</div>';
		               
		var i = $(id).attr('file-counter');
		if (!i){
			$(id).empty();
			
			i = 0;
		}
		
		i++;
		
		$(id).attr('file-counter', i);
		
		$(id).prepend(template);
	},
	init:function(id){
		// $(id).empty()
	},
	updateFileStatus: function(i, status, message){
		// $('#demo-file' + i).removeClass()
		$('#demo-file' + i).find('span.demo-file-status').html(message).removeClass('demo-file-status-success').addClass('demo-file-status-' + status);
	},
	
	updateFileProgress: function(i, percent){
		$('#demo-file' + i).find('div.progress-bar').width(percent);
		
		$('#demo-file' + i).find('span.sr-only').html(percent + ' Complete');
	},
	hideProgress:function(i,percent){
		$('#demo-file' + i).hide()
	},
	
	humanizeSize: function(size) {
      var i = Math.floor( Math.log(size) / Math.log(1024) );
      return ( size / Math.pow(1024, i) ).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i];
    }

  }, $.danidemo);
})(jQuery, this);