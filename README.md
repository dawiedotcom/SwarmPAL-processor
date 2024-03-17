# SwarmPAL-processor

## Build and run the dashboard (Docker/Podman)

Build the image:
```
podman build -t swarmpal-processor .
```

Get a VirES access token from https://vires.services/accounts/tokens/ and store it in a file called `.env`:
```
VIRES_TOKEN=.....
```

To start the [panel server](https://panel.holoviz.org/how_to/server/commandline.html):
```
podman compose up
```

or equivalently:
```
podman run --rm -it -p 5006:5006 --env-file .env -d swarmpal-processor /app/start-dashboard.sh
```


## Install in venv (uv example)

(Tested with Python 3.12)

Create and activate venv, and install pip packages:
```
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Manually alter `requirements.in` if needed and update `requirements.txt`:
```
uv pip compile requirements.in -o requirements.txt
```

- Develop using Jupyter: `jupyter-lab`
- Test dashboard: `panel serve app.ipynb`
