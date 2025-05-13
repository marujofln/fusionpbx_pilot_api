#!/bin/sh
export PYTHONPATH=$PYTHONPATH:$(pwd)
fastapi run fusionpbx_pilot_api/services/restapi.py