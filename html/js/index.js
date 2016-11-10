var comp_select = document.getElementById('comp_select');
var mode_select = document.getElementById('mode_select');
var date_select = document.getElementById('date_select');
var user_select = document.getElementById('user_select');
var playlist = document.getElementById('playlist');
var player = document.getElementById('player');

var movies = [];
var online_timeout_id = 0;

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
};

function get_dates() {	
	show_elem(onlineimg, false);
	var xmlHttp = get_xmlHttp_obj();
	xmlHttp.open('GET', '/api/archive' + '?act=get_dates', true);
	xmlHttp.onreadystatechange = function() {
		if (xmlHttp.readyState == 4) {
			xmlHttp.onreadystatechange = null; // plug memory leak
			if (xmlHttp.status == 200) {
				var html_data = '';
				var obj_data = JSON.parse(xmlHttp.responseText);
				for (var d of obj_data) {
					html_data += '<option value="' + d	+ '">' + d + '</option>';
				}
				date_select.innerHTML = html_data;
				get_comps();
			}
		};
	}
	xmlHttp.send(null);
}

function get_comps() {
	show_elem(onlineimg, false);
	var xmlHttp = get_xmlHttp_obj();
	xmlHttp.open('GET', '/api/archive' + '?act=get_comps', true);
	xmlHttp.onreadystatechange = function() {
		if (xmlHttp.readyState == 4) {
			xmlHttp.onreadystatechange = null; // plug memory leak
			if (xmlHttp.status == 200) {
				var html_data = '';
				var obj_data = JSON.parse(xmlHttp.responseText);

				for (var c of obj_data) {
					html_data += '<option value="' + c + '">' + c + '</option>';
				}
				comp_select.innerHTML = html_data;
				get_users();
			}
		}
	}
	xmlHttp.send(null);
}

function get_users() {
	show_elem(onlineimg, false);
	var xmlHttp = get_xmlHttp_obj();	
	xmlHttp.open('GET', '/api/archive' + '?act=get_users&' + '&comp=' + comp_select.value, true);
	xmlHttp.onreadystatechange = function() {
		if (xmlHttp.readyState == 4) {
			xmlHttp.onreadystatechange = null; // plug memory leak
			if (xmlHttp.status == 200) {
				var html_data = '';
				var obj_data = JSON.parse(xmlHttp.responseText);

				for (var u of obj_data) {
					html_data += '<option value="' + u + '">' + u + '</option>';
				}
				user_select.innerHTML = html_data;
				get_movies();
			}
		}
	}
	xmlHttp.send(null);
}

function get_movies() {
	var xmlHttp = get_xmlHttp_obj();
	movies.length = 0;
	xmlHttp.open('GET', '/api/archive' + '?act=get_movies' + '&date=' + date_select.value + '&comp=' + comp_select.value + '&user=' + user_select.value, true);
	xmlHttp.onreadystatechange = function() {
		if (xmlHttp.readyState == 4) {
			xmlHttp.onreadystatechange = null; // plug memory leak
			if (xmlHttp.status == 200) {
				var obj_data = JSON.parse(xmlHttp.responseText);
				var html_data = '';
				for (var i = 0; i < obj_data.length; i++) {
					var start_end = /([^/.]+)\./.exec(obj_data[i])[1];
					var title = [];
					for (var t of start_end.split('-')) {
						title.push(hhmmss_format(t));						
					}
					title = title.join(' - ');
					movies[i] = obj_data[i];
					html_data += '<span onclick="show_archive(' + i + ');">&nbsp;' + title + '&nbsp;<br></span>';
				}
				playlist.innerHTML = html_data;
			}
		}
	}
	xmlHttp.send(null);		
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
	videoPlayer.set_next_movie(movie_index+1);
	
	var playlist = document.getElementById('playlist').children;
	for (var i = 0; i < playlist.length; i++) {
		if (i != movie_index) {
			playlist[i].classList.remove('archive_hlight');
		} else {
			playlist[i].classList.add('archive_hlight');
		}
	}
	player.innerHTML = "<div id='player_obj'></div>";
	videoPlayer.set_video_player({
		id : 'player_obj',
		name : movies[movie_index],
		width : '100%',
		height : '100%'
	})	
	if (document.getElementById('html5player')) {
		var html5player = document.getElementById('html5player');
		html5player.onloadeddata=html5VideoLoaded;				
		html5player.onseeked=html5VideoScrolled;
		html5player.ontimeupdate=html5VideoProgress;
		html5player.onended=html5VideoFinished;
		html5player = null;
	}
}

function show_online() {	
	function request() {
		var xmlHttp = get_xmlHttp_obj();
		xmlHttp.open('GET', '/api/online' + '?comp=' + comp_select.value + '&user=' + user_select.value, true);
		xmlHttp.onreadystatechange = function() {
			if (xmlHttp.readyState == 4) {
				xmlHttp.onreadystatechange = null; // plug memory leak
				if (xmlHttp.status == 200) {
					var obj_data = JSON.parse(xmlHttp.responseText);
					if (obj_data.length > 0) {
						show_elem(onlineimg, true);
						onlineimg.src=obj_data[0];						
					} else {
						show_elem(onlineimg, false);
					}						
				}
			}
			
		}
		xmlHttp.send(null);
	}
	mode_select.selectedIndex = 0;
	player.innerHTML = '';
	player.appendChild(onlineimg);	
	player.appendChild(loadingimg);	
	clearTimeout(online_timeout_id);	
	online_timeout_id=setTimeout(function() {
		if (mode_select.selectedIndex==0) {
			request();
			setTimeout(arguments.callee,2000);
		}	
	}, 2000);
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
	show_online()
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
    
    function get_time() {
        return tm;
    }
    
    function set_play_accel(accel) {
        current_play_accel = accel;
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
            if (document.getElementById('flashplayer')) {			
                var flashplayer=document.getElementById('flashplayer');
                switch (e.which) {
                case 39:
                    if (flashplayer['jsScroll']) {
                        tm+=1;
                        if (tm<=movie_duration-1)
                            flashplayer.jsScroll(tm);
                    }
                    break;
                case 37:
                    if (flashplayer['jsScroll']) {
                        tm-=1;	
                        if (tm>=1)
                            flashplayer.jsScroll(tm);
                    }
                    break;
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
                    break;
                }                
                flashplayer=null;
            }
        }
    }
    
    function html5VideoProgress() {
        if (document.getElementById('html5player')) {
            var html5player=document.getElementById('html5player');
            var rate=1;
            if (current_play_accel<0)
                rate=0.5;
            else if (current_play_accel>1)
                rate=2;
                
            html5player.playbackRate=rate;
            tm=html5player.currentTime;
            html5player=null;
        }	
    }
    
    function html5VideoScrolled() {
        if (document.getElementById('html5player')) {
            var html5player=document.getElementById('html5player');
            tm=html5player.currentTime;            
            html5player=null;
        }
    }
    
    function html5VideoFinished() {
        tm=0;
        show_archive(next_movie);
    }
    
    function html5playerPlayPause() {
        if (document.getElementById('html5player')) {
            var html5player=document.getElementById('html5player');
            if (html5player.paused)
                html5player.play();
            else
                html5player.pause();
            html5player=null;
        }	
    }
    
    function html5VideoLoaded() {
        document.onkeydown = function(e) {
            if (document.getElementById('html5player')) {
                var html5player=document.getElementById('html5player'); 
                switch (e.which) {
                case 39:
                    tm+=1;
                    if (tm<=html5player.duration-1)
                        html5player.currentTime=tm;
                    break;
                case 37:
                    tm-=1;
                    if (tm>=1)
                        html5player.currentTime=tm;
                    break;
                case 32:
                    html5playerPlayPause();
                    tm=html5player.currentTime;
                    break;
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

		var canplay = checkVideo(getFileExtension(params.name));

		if (canplay == "html5") {
			document.getElementById(params.id).innerHTML = '<video id="html5player" width="'
					+ params.width
					+ '" height="'
					+ params.height
					+ '" autoplay controls ></video>';

			var html5player = document.getElementById('html5player');
			html5player.innerHTML = "<p><a href=\"" + document.URL + params.name
					+ "\" target='_blank'>DOWNLOAD: "
					+ params.name.split(/(\\|\/)/g).pop() + "</a></p>";

			html5player.src = params.name;
		} else if (canplay == "flash") {
			var id = ID();
			document.getElementById(params.id).innerHTML = '<div id="' + id
					+ '"> </div>';
			document.getElementById(id).innerHTML = "<p><a href=\"" + document.URL
					+ params.name + "\" target='_blank'>DOWNLOAD: "
					+ params.name.split(/(\\|\/)/g).pop() + "</a></p>";

			var flashvars = {
				video_url : params.name,
				permalink_url : document.URL + params.name,
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
					+ document.URL + params.name + "\" target='_blank'>DOWNLOAD: "
					+ params.name.split(/(\\|\/)/g).pop() + "</a></p>";
		}
	}
		
    // /////////////////EXPORT METHODS//////////////////////////////
    
    return {
        set_video_player: set_video_player,
        set_cur_event_secs: set_cur_event_secs,
        set_next_movie: set_next_movie,
        set_movie_duration: set_movie_duration,
        get_time: get_time,
        set_play_accel: set_play_accel,
        
        // /////////////////FLASHPLAYER EVENTS//////////////////////////////

        ktVideoProgress: ktVideoProgress,
        ktVideoFinished: ktVideoFinished,
        ktVideoScrolled: ktVideoScrolled,
        ktVideoStarted: ktVideoStarted,
        ktVideoPaused: ktVideoPaused,
        ktVideoStopped: ktVideoStopped,
        ktPlayerLoaded: ktPlayerLoaded,

        // ///////////////HTML5PLAYER EVENTS/////////////////////////

        html5VideoProgress: html5VideoProgress,
        html5VideoScrolled: html5VideoScrolled,
        html5VideoFinished: html5VideoFinished,
        html5playerPlayPause: html5playerPlayPause,
        html5VideoLoaded: html5VideoLoaded 
    }
}();

var ktVideoProgress = videoPlayer.ktVideoProgress;
var ktVideoFinished = videoPlayer.ktVideoFinished;
var ktVideoScrolled = videoPlayer.ktVideoScrolled;
var ktVideoStarted = videoPlayer.ktVideoStarted;
var ktVideoPaused = videoPlayer.ktVideoPaused;
var ktVideoStopped = videoPlayer.ktVideoStopped;
var ktPlayerLoaded = videoPlayer.ktPlayerLoaded;
var html5VideoProgress = videoPlayer.html5VideoProgress;
var html5VideoScrolled = videoPlayer.html5VideoScrolled;
var html5VideoFinished = videoPlayer.html5VideoFinished;
var html5playerPlayPause = videoPlayer.html5playerPlayPause;
var html5VideoLoaded = videoPlayer.html5VideoLoaded;

// ////////////////////////////



init();
