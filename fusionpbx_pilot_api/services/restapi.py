# -*- coding: utf-8 -*-
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fusionpbx_pilot_api.__init__ import __version__
from fusionpbx_pilot_api.routers import domains, extensions, me, provisioning
from fusionpbx_pilot_api.settings import Settings

config = Settings()

logging.basicConfig(
    format='%(asctime)s [WEBSERVER] %(levelname)-8s %(message)s',
    level=logging.DEBUG,
)


app = FastAPI(
    title='FusionPBX Pilot API',
    version=__version__,
)
origins = ['http://localhost', 'http://localhost:8000']


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# routers include
app.include_router(me.router_v1)
app.include_router(domains.router_v1)
app.include_router(extensions.router_v1)
app.include_router(provisioning.router_v1)
