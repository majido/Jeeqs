from google.appengine.dist import use_library
use_library('django', '1.3')

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

# uncomment to enable app stats
#def webapp_add_wsgi_middleware(app):
#    from google.appengine.ext.appstats import recording
#    app = recording.appstats_wsgi_middleware(app)
#    return app

appstats_MAX_STACK = 30
appstats_MAX_LOCALS = 20
appstats_MAX_REPR = 1000
appstats_MAX_DEPTH = 20
