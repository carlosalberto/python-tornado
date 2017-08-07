from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado import gen

import opentracing
import tornado_opentracing


tornado_opentracing.init_tracing()

# Your OpenTracing-compatible tracer here.
tracer = opentracing.Tracer()


class MainHandler(RequestHandler):
    def get(self):
        self.write({'status': 'ok'})


class StoryHandler(RequestHandler):
    @gen.coroutine
    def get(self, story_id):
        res = yield AsyncHTTPClient().fetch('http://127.0.0.1:8080/child')
        self.write({'status': 'fetched'})


class ChildHandler(RequestHandler):
    def get(self):
        self.write('{}')


app = Application([
        (r'/', MainHandler),
        (r'/story/([0-9]+)', StoryHandler),
        (r'/child', ChildHandler),
    ],
    opentracing_tracer=tornado_opentracing.TornadoTracer(tracer),
    opentracing_trace_all=True,
    opentracing_trace_client=True,
)
app.listen(8080)
IOLoop.current().start()
