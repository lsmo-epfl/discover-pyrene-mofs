#!/bin/bash -e
set -x

# This script is executed whenever the docker container is (re)started.
#===============================================================================
panel serve detail_pyrenemofs figure_pyrenemofs select_pyrenemofs \
    --port 5006                 \
    --allow-websocket-origin "*" \
    --prefix "$BOKEH_PREFIX" \
    --use-xheaders
# --allow-websocket-origin discover.materialscloud.org 

#EOF
