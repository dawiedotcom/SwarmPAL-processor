#!/bin/bash
set -e

# Set the token
viresclient set_token https://vires.services/ows $VIRES_TOKEN

# Execute the CMD instruction
exec "$@"