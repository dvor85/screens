var comp_select = document.getElementById('comp_select');
var mode_select = document.getElementById('mode_select');
var date_select = document.getElementById('date_select');
var user_select = document.getElementById('user_select');
var playlist = document.getElementById('playlist');
var player = document.getElementById('player');
var api_url = '/web';

var movies = [];
var online_timeout_id = 0;
var movies_timeout_id = 0;

var loadingimg = new Image();
loadingimg.src = 'media/loading.gif';
loadingimg.style.position = 'absolute';
loadingimg.style.width = '32px';
loadingimg.style.height = '32px';
loadingimg.style.bottom = Math.round(player.clientHeight / 2) - 10 + 'px';
loadingimg.style.right = Math.round(player.clientWidth / 2) - 10 + 'px';
loadingimg.style.zIndex = -1;
loadingimg.style.border = 0;

var onlineimg = new Image();
onlineimg.style.width = '100%';
onlineimg.style.height = '100%';
onlineimg.style.zIndex = 1;
onlineimg.style.border = 0;
onlineimg.onerror = function() {show_elem(this, false);}

function pad_out(val, pad) {

    // A function to implement zero fill string padding
    //
    // expects :
    // 'val' ... the object to be padded
    // 'pad' ... the required width
    //
    // returns :
    // 'string' ... the zero filled padded string

    var fill = '00000000000000000000';
    if (String(val).length < pad) {
    	val = fill.substr(0, pad - String(val).length) + String(val);
    }
    return String(val);
}

function pad_out2(val) {
    // pad to 2 digit with zero
    return pad_out(val, 2);
};

function pad_out4(val) {
    // pad to 4 digit with zero
    return pad_out(val, 4);
};

function pad_out6(val) {
    // pad to 6 digit with zero
    return pad_out(val, 6);
};

function secs_hh_mm_ss(secs) {

    // A function that convers a seconds count to a 'HH:MM:SS' string
    //
    // expects :
    // 'secs' ... a seconds count
    //
    // returns :
    // 'time' ... a 'HH:MM:SS' string

    var hh = parseInt(secs / (60 * 60), 10);
    var mm = parseInt((secs - (hh * 60 * 60)) / 60, 10);
    var ss = parseInt(secs - (hh * 60 * 60) - (mm * 60), 10);
    return pad_out2(hh) + ':' + pad_out2(mm) + ':' + pad_out2(ss);
}

function hhmmss_secs(hhmmss) {
    // convert HHMMSS string to an integer number
    hhmmss = pad_out6(hhmmss);
    var hh=parseInt(hhmmss.slice(0, 2), 10);
    var mm=parseInt(hhmmss.slice(2, 4), 10);
    var ss=parseInt(hhmmss.slice(4, 6), 10);
    return (hh * 60 * 60) + (mm * 60) + ss;
}

function hhmmss_format(hhmmss) {
    // convert HHMMSS string to a 'HH:MM:SS'
    hhmmss = pad_out6(hhmmss);
    var hh=parseInt(hhmmss.slice(0, 2), 10);
    var mm=parseInt(hhmmss.slice(2, 4), 10);
    var ss=parseInt(hhmmss.slice(4, 6), 10);
    return pad_out2(hh) + ':' + pad_out2(mm) + ':' + pad_out2(ss);
}

function yyyymmdd_format(yyyymmdd) {
    // convert yyyymmdd string to a 'yyyy-mm-dd'
	yyyymmdd = pad_out(yyyymmdd, 8);
    var yyyy=parseInt(yyyymmdd.slice(0, 4), 10);
    var mm=parseInt(yyyymmdd.slice(4, 6), 10);
    var dd=parseInt(yyyymmdd.slice(6, 8), 10);
    return pad_out4(yyyy) + '-' + pad_out2(mm) + '-' + pad_out2(dd);
}

function show_elem(elem, visible) {
	if (elem) {
		if (visible === true) {
			elem.style.visibility = 'visible';
		} else {
			elem.style.visibility = 'hidden';
		}
	}
}

function get_xmlHttp_obj() {
	var xmlHttp = null;
	try { // Firefox, Opera 8.0+, Safari
		xmlHttp = new XMLHttpRequest();
	} catch (e) { // Internet Explorer
		try {
			xmlHttp = new ActiveXObject("Msxml2.XMLHTTP");
		} catch (e) { // Internet Explorer 5.5
			xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
		}
	}
	return xmlHttp;
}

function json_request(url, json, callback){
	var xmlHttp = get_xmlHttp_obj();
	var jreq = json;
	var json = JSON.stringify(jreq);
	xmlHttp.open('POST', url, true);
	xmlHttp.setRequestHeader("Content-type", "application/json");
	xmlHttp.onreadystatechange = function() {
		if (xmlHttp.readyState == 4) {
			xmlHttp.onreadystatechange = null; // plug memory leak
			if (xmlHttp.status == 200) {
				if (callback) {
					var jres = JSON.parse(xmlHttp.responseText);
					if (jres.id != jreq.id){
						console.log("Invalid ID");
						return false;
					}
					if (jres.error) {
						console.log(jres.error.message);
						return false;
					}
					
					callback(jres.result);
					return true;
				}
			}
		}
	}	
	xmlHttp.send(json);
}

function get_dates() {	
	function fill_dates(obj_data) {
		var html_data = '';
		for (var d of obj_data) {
			html_data += '<option value="' + d	+ '">' + yyyymmdd_format(d) + '</option>';
		}
		date_select.innerHTML = html_data;
	}
	
	show_elem(onlineimg, false);
	var jreq = {jsonrpc: '2.0', method: 'archive', id: Math.random(), params: {act: "get_dates"} }
	json_request(api_url, jreq, fill_dates)
}

function get_comps() {
	function fill_comps(obj_data) {
		var html_data = '';
		for (var c in obj_data) {
			if (obj_data.hasOwnProperty(c)) {
				html_data += '<option value="' + c + '">' + obj_data[c] + '</option>';
			}
		}
		comp_select.innerHTML = html_data;
		get_users();
	}
	show_elem(onlineimg, false);
	var jreq = {jsonrpc: '2.0', method: 'archive', id: Math.random(), params: {act: "get_comps"} }
	json_request(api_url, jreq, fill_comps);
}

function get_users() {
	function fill_users(obj_data) {
		var html_data = '';
		for (var u of obj_data) {
			html_data += '<option value="' + u + '">' + u + '</option>';
		}
		user_select.innerHTML = html_data;
		get_movies();
	}
	
	show_elem(onlineimg, false);
	var jreq = {jsonrpc: '2.0', method: 'archive', id: Math.random(), params: {act: "get_users", comp: comp_select.value} }
	json_request(api_url, jreq, fill_users);
}

function get_movies() {
	function fill_movies(obj_data) {
		var html_data = '';
		for (var i = 0; i < obj_data.length; i++) {
			try {
				var start_end = /([^/.]+)\./.exec(obj_data[i])[1];
				var title = [];
				for (var t of start_end.split('-')) {
					title.push(hhmmss_format(t));						
				}
				title = title.join(' - ');
				movies[i] = obj_data[i];
				html_data += '<span onclick="show_archive(' + i + ');">&nbsp;' + title + '&nbsp;<br></span>';
			} catch (e) {
				console.log(e);
			}
									
		}
		playlist.innerHTML = html_data;
		var movie_index = videoPlayer.get_next_movie_id() - 1;
		playlist_hlight(movie_index);
	}
	
	movies.length = 0;
	if (mode_select.selectedIndex==1) {
		videoPlayer.html5playerStop();
		// show_archive();
	}
	clearTimeout(movies_timeout_id);
	movies_timeout_id=setTimeout(function() {
		var _params = {act: "get_movies", 
					   comp: comp_select.value,
					   user: user_select.value,
					   date: date_select.value					   
		}
		var jreq = {jsonrpc: '2.0', method: 'archive', id: Math.random(), params: _params}
		json_request(api_url, jreq, fill_movies);
		clearTimeout(movies_timeout_id);
		movies_timeout_id = setTimeout(arguments.callee, 60000);
	}, 10);
}


function playlist_hlight(movie_index) {
	videoPlayer.set_next_movie(movie_index+1);
	var lines = playlist.children;
	for (var i = 0; i < lines.length; i++) {
		if (i != movie_index) {
			lines[i].classList.remove('playlist_hlight');
		} else {
			lines[i].classList.add('playlist_hlight');
		}
	}
}


function show_archive(movie_index) {
	show_elem(onlineimg, false);
	mode_select.selectedIndex = 1;
	clearTimeout(online_timeout_id);
	if (movies.length == 0) {
		return;
	}
	if (!movie_index) {
		movie_index = 0;
	}

	playlist_hlight(movie_index);
	
	player.innerHTML = "<div id='player_obj'></div>";
    var rate = document.getElementById('playback_rate').value;
	videoPlayer.set_video_player({
		id : 'player_obj',
		src : movies[movie_index],
		width : '100%',
		height : '100%',
        config:{
            autoplay:true, 
            controls:true, 
            muted:true, 
            playbackRate:rate
        }
    });	
	
	var html5player = document.getElementById('html5player');
	if (html5player) {
		html5player.onloadeddata=videoPlayer.html5playerLoaded;				
		html5player.onseeked=videoPlayer.html5playerScrolled;
		html5player.ontimeupdate=videoPlayer.html5playerProgress;
		html5player.onended=videoPlayer.html5playerFinished;
		html5player.onclick=videoPlayer.html5playerPlayPause;
		html5player = null;
	}
}

function show_online() {
	function show(obj_data) {
		if (obj_data.length > 0) {
			show_elem(onlineimg, true);
			onlineimg.src=obj_data[0];						
		} else {
			show_elem(onlineimg, false);
		}		
	}
	
	mode_select.selectedIndex = 0;
	player.innerHTML = '';
	player.appendChild(onlineimg);	
	player.appendChild(loadingimg);	
	
	clearTimeout(online_timeout_id);	
	online_timeout_id=setTimeout(function() {
		if (mode_select.selectedIndex==0) {
			var _params = {comp: comp_select.value,
						   user: user_select.value,						   					   
			}
			var jreq = {jsonrpc: '2.0', method: 'online', id: Math.random(), params: _params}
			json_request(api_url, jreq, show);
			clearTimeout(online_timeout_id);
			online_timeout_id = setTimeout(arguments.callee, 2000);
		}	
	}, 1000);
}

function change_mode() {
	show_elem(onlineimg, false);
	if (mode_select.selectedIndex == 1) {
		show_archive();
	} else {
		show_online();
	}
}


function init() {
	get_dates();
	get_comps();
	show_online();
}



// /////////////////////////////


videoPlayer = function() {

    var tm=0;
    var paused=false;
    var movie_duration=0;
    var next_movie=0;
    var cur_event_secs=0;
    var current_play_accel=1;
    
    function set_cur_event_secs(secs) {
        cur_event_secs = secs;
    }
    
    function set_next_movie(movie_id) {
        next_movie = movie_id;
    }
    
    function set_movie_duration(dur) {
        movie_duration = dur;
    }
    
    function set_play_accel(accel) {
        current_play_accel = accel;
    }
    
    function get_time() {
        return tm;
    }
    
    function get_next_movie_id() {
        return next_movie;
    }
    
    function ktVideoProgress(time) {
    // вызывается каждую секунду проигрывания видео
        tm=parseInt(time,10);
        if ((current_play_accel>0)&&(current_play_accel<5)){
            if (document.getElementById('flashplayer')['jsScroll']) {
                document.getElementById('flashplayer').jsScroll(++tm);
            }
        }        
    }
    
    function ktVideoFinished() {
        tm=0;
        show_archive(next_movie);
    }
    
    function ktVideoScrolled(time) {
    // вызовется при перемотке видео
        tm=parseInt(time,10);        
    }
    
    function ktVideoStarted() {
    // вызовется при нажатии на кнопку play
        paused=false;
    }
    
    function ktVideoPaused() {
    // вызовется при нажатии на кнопку pause
        paused=true;
    }
    
    function ktVideoStopped() {
    // вызовется при нажатии на кнопку stop
        paused=true;
    }   

    function ktPlayerLoaded() {
        tm=0;
        document.onkeydown = function(e) {
        	var flashplayer=document.getElementById('flashplayer');
            if (flashplayer) {			
                switch (e.which) {
                case 39:
                    if (flashplayer['jsScroll']) {
                        tm+=1;
                        if (tm<=movie_duration-1)
                            flashplayer.jsScroll(tm);
                    }
                    return false;
                case 37:
                    if (flashplayer['jsScroll']) {
                        tm-=1;	
                        if (tm>=1)
                            flashplayer.jsScroll(tm);
                    }
                    return false;
                case 32:
                    if (paused) {
                        if (flashplayer['jsPlay']) {
                            flashplayer.jsPlay();
                            paused=false;
                        }
                    }
                    else {
                        if (flashplayer['jsPause']) {
                            flashplayer.jsPause();
                            paused=true;
                        }
                    }
                    return false;
                }                
                flashplayer=null;
            }
        }
    }
    
    function html5playerProgress() {
        var rate = document.getElementById('playback_rate').value;
            
        this.playbackRate=rate;
        tm=this.currentTime;
    }
    
    function html5playerScrolled() {
        tm=this.currentTime;            
    }
    
    function html5playerFinished() {
        tm=0;
        if (movies[next_movie]) {
        	this.src = movies[next_movie];
        	playlist_hlight(next_movie);
        }
    }
    
    function html5playerPlayPause() {
    	var html5player=document.getElementById('html5player'); 
        if (html5player) {
            if (html5player.paused)
                html5player.play();
            else
                html5player.pause();
            html5player=null;
        }	
    }
    
    function html5playerStop() {
    	var html5player=document.getElementById('html5player');
    	if (html5player) {
    		html5player.src=null;
    		// html5player.currentTime=html5player.duration;
    		// tm=html5player.currentTime;
    	}
    	html5player=null;
    }
    
    function html5playerLoaded() {
        document.onkeydown = function(e) {
        	var html5player=document.getElementById('html5player'); 
            if (html5player) {
                switch (e.which) {
                case 39:
                    tm+=1;
                    if (tm<=html5player.duration-1)
                        html5player.currentTime=tm;
                    return false;
                case 37:
                    tm-=1;
                    if (tm>=1)
                        html5player.currentTime=tm;
                    return false;
                case 32:
                	html5playerPlayPause();
                    tm=html5player.currentTime;
                    return false;
                }                
                html5player=null;
            }
        }
    }
    
    function set_video_player(params) {
		function getFileExtension(filename) {
			var ext = /^.+\.([^.]+)$/.exec(filename);
			return ext == null ? "" : ext[1];
		}

		function ID() {
			return '_' + Math.random().toString(36).substr(2, 9);
		}

		function checkVideo(format) {
			switch (format) {
			case 'mp4':
				var vidTest = document.createElement("video");
				if (vidTest.canPlayType) {
					h264Test = vidTest
							.canPlayType('video/mp4; codecs="avc1.42E01E, mp4a.40.2"'); // mp4
																						// format
					if (!h264Test) { // if it doesnot support .mp4 format
						return "flash"; // play flash
					} else {
						if (h264Test == "probably") { // supports .mp4 format
							return "html5"; // play HTML5 video
						} else {
							return "flash"; // play flash video if it doesnot
											// support any of them.
						}
					}
				}
			case 'ogv':
				var vidTest = document.createElement("video");
				if (vidTest.canPlayType) {
					oggTest = vidTest
							.canPlayType('video/ogg; codecs="theora, vorbis"'); // ogg
																				// format
					if (!oggTest) { // if it doesnot support
						return "none"; // play flash
					} else {
						if (oggTest == "probably") { // supports
							return "html5"; // play HTML5 video
						} else {
							return "none"; // play flash video if it doesnot
											// support any of them.
						}
					}
				}
			case 'webm':
				var vidTest = document.createElement("video");
				if (vidTest.canPlayType) {
					webmTest = vidTest
							.canPlayType('video/webm; codecs="vp8.0, vorbis"'); // webm
																				// format
					if (!webmTest) { // if it doesnot support
						return "none"; // play flash
					} else {
						if (webmTest == "probably") { // supports
							return "html5"; // play HTML5 video
						} else {
							return "none"; // play flash video if it doesnot
											// support any of them.
						}
					}
				}
				break;
			case 'flv':
			case 'swf':
				return "flash";
				break;
			default:
				return "none";
			}
		}

		var canplay = checkVideo(getFileExtension(params.src));

		if (canplay == "html5") {
			document.getElementById(params.id).innerHTML = '<video id="html5player" width="'
					+ params.width
					+ '" height="'
					+ params.height
                    + '"</video>';
            
			var html5player = document.getElementById('html5player');
            for (var key in params.config) {
                if (params.config.hasOwnProperty(key))
                    try {
                        html5player[key] = params.config[key];
                    } catch (e) {};
            }
			html5player.innerHTML = "<p><a href=\"" + document.URL + params.src
					+ "\" target='_blank'>DOWNLOAD: "
					+ params.src.split(/(\\|\/)/g).pop() + "</a></p>";

			html5player.src = params.src;
		} else if (canplay == "flash") {
			var id = ID();
			document.getElementById(params.id).innerHTML = '<div id="' + id
					+ '"> </div>';
			document.getElementById(id).innerHTML = "<p><a href=\"" + document.URL
					+ params.src + "\" target='_blank'>DOWNLOAD: "
					+ params.src.split(/(\\|\/)/g).pop() + "</a></p>";

			var flashvars = {
				video_url : params.src,
				permalink_url : document.URL + params.src,
				bt : 5,
				scaling : 'fill',
				hide_controlbar : 0,
				flv_stream : false,
				autoplay : true,
				js : 1
			};
			var fparams = {
				allowfullscreen : 'true',
				allowscriptaccess : 'always',
				quality : 'best',
				bgcolor : '#000000',
				scale : 'exactfit'
			};
			var fattributes = {
				id : 'flashplayer',
				name : 'flashplayer'
			};
			swfobject.embedSWF('media/kt_player.swf', id, params.width, params.height,
					'9.124.0', 'media/expressInstall.swf', flashvars, fparams,
					fattributes);
		} else {
			document.getElementById(params.id).innerHTML = "<p><a href=\""
					+ document.URL + params.src + "\" target='_blank'>DOWNLOAD: "
					+ params.src.split(/(\\|\/)/g).pop() + "</a></p>";
		}
	}
		
    // /////////////////EXPORT METHODS//////////////////////////////
    
    return {
        set_video_player: set_video_player,
        set_cur_event_secs: set_cur_event_secs,
        set_next_movie: set_next_movie,
        set_movie_duration: set_movie_duration,
        set_play_accel: set_play_accel,
        get_time: get_time,
        get_next_movie_id: get_next_movie_id,
        
        
        // /////////////////FLASHPLAYER EVENTS//////////////////////////////

        ktVideoProgress: ktVideoProgress,
        ktVideoFinished: ktVideoFinished,
        ktVideoScrolled: ktVideoScrolled,
        ktVideoStarted: ktVideoStarted,
        ktVideoPaused: ktVideoPaused,
        ktVideoStopped: ktVideoStopped,
        ktPlayerLoaded: ktPlayerLoaded,

        // ///////////////HTML5PLAYER EVENTS/////////////////////////

        html5playerProgress: html5playerProgress,
        html5playerScrolled: html5playerScrolled,
        html5playerFinished: html5playerFinished,
        html5playerPlayPause: html5playerPlayPause,
        html5playerStop: html5playerStop,
        html5playerLoaded: html5playerLoaded 
        
    }
}();

var ktVideoProgress = videoPlayer.ktVideoProgress;
var ktVideoFinished = videoPlayer.ktVideoFinished;
var ktVideoScrolled = videoPlayer.ktVideoScrolled;
var ktVideoStarted = videoPlayer.ktVideoStarted;
var ktVideoPaused = videoPlayer.ktVideoPaused;
var ktVideoStopped = videoPlayer.ktVideoStopped;
var ktPlayerLoaded = videoPlayer.ktPlayerLoaded;


// ////////////////////////////



init();
