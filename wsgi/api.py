from cgi import escape
import os ,sys

selfdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(selfdir)
from core import logger, defines
from core.config import config


log = logger.getLogger(__name__, config['LOGLEVEL'])


def application(env, start_response):
    
    try:
        status = '200 OK'
        body = ''        
        path_info = escape(env['PATH_INFO'])      
                
        if path_info == "/image":      
            from wsgi.image import ImageStore
            body = ImageStore(env).main()
        elif path_info == "/script":
            from wsgi.script import Script
            body = Script(env).main()
        elif path_info == "/upload":
            from wsgi.upload import Upload 
            body = Upload(env).main()
        elif path_info == "/online":      
            from wsgi.online import Online
            body = Online(env).main()
        elif path_info == "/archive":
            from wsgi.archive import Archive 
            body = Archive(env).main()    
                    
        elif path_info == "/env":
            for k,v in env.items():
                body += '{0}: {1}\n'.format(k,v)
        else:
            status = '404 Error'
            body = status
            
        if body is None:
            body = ''
                
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        status = '500 Error'
        body = 'error {type}: {value}'.format(**{'type':exc_type, 'value':exc_value}) 
        log.error(status)      
    finally:
        if body is None:
            body = '' 
        start_response(status, [('Content-type', 'text/plain'),
                                ('Content-Length', str(len(body)))])
    return [body]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8080, application)
    log.debug("Serving on port 8080...")
    httpd.serve_forever()
