from cgi import parse_qs, escape
import datetime
import time
import urllib2
import os ,sys
import logger

log = logger.Logger('wsgi')

def application(env, start_response):
    selfdir = os.path.abspath(os.path.dirname(__file__))  
    try:
        status = '200 OK'
        body = ''        
        path_info = escape(env['PATH_INFO'])      
                
        if path_info == "/image":      
            from image import ImageStore
            body = ImageStore(selfdir, env).main()
        elif path_info == "/script":
            from script import Script
            body = Script(selfdir, env).main()
        elif path_info == "/upload":
            from upload import Upload 
            body = Upload(selfdir, env).main()
        elif path_info == "/env":
            for k,v in env.items():
                body += '{0}: {1}\n'.format(k,v)        
                    
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        status = '500 Error'
        body = 'error {type}: {value}'.format(**{'type':exc_type, 'value':exc_value}) 
        log.exception(status)      
    finally:
        start_response(status, [('Content-type', 'text/plain'),
                                ('Content-Length', str(len(body)))])
    return [body]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8080, application)
    print "Serving on port 8080..."
    httpd.serve_forever()
