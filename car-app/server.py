import os
import json
import time
import asyncio

import tornado.ioloop
import tornado.web
import tornado.gen

import numpy as np
from PIL import Image
from io import BytesIO

import config


class VideoServer(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/video", VideoAPI)
        ]
        super().__init__(handlers, **{'debug': config.SERVER_DEBUG})

    def update(self, port=config.SERVER_PORT):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.port = int(port)
        self.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()

    def run_threaded(self, img_arr=None):
        self.img_arr = img_arr

    def run(self, img_arr=None):
        self.img_arr = img_arr

    def shutdown(self):
        tornado.ioloop.IOLoop.instance().stop()


class VideoAPI(tornado.web.RequestHandler):

    async def get(self):

        self.set_header("Content-type", "multipart/x-mixed-replace;boundary=--boundarydonotcross")

        self.last_time = time.time()

        interval = config.SERVER_INTERVAL
        while True:

            if time.time() > self.last_time + interval:

                try:

                    img = Image.fromarray(np.uint8(self.application.img_arr))
                    bytes = BytesIO()
                    img.save(bytes, format='jpeg')
                    frame = bytes.getvalue()

                    self.write("--boundarydonotcross\n")
                    self.write("Content-type: image/jpeg\r\n")
                    self.write("Content-length: %s\r\n\r\n" % len(frame))
                    self.write(frame)
                    self.last_time = time.time()

                    await self.flush()

                except tornado.iostream.StreamClosedError:
                    pass
                except Exception as e:
                    raise e
        else:

            await tornado.gen.sleep(interval)
