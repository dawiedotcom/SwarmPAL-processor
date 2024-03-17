#!/bin/bash
viresclient set_token https://vires.services/ows $VIRES_TOKEN
panel serve app.ipynb
