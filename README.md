# SwarmPAL-processor

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

## Run the processor

NB: These are not stable instructions yet!

[Configure the token access](https://viresclient.readthedocs.io/en/latest/cli.html#configuration) on your machine if not already done (stores file at `~/.viresclient.ini`):
```
viresclient set_token https://vires.services/ows
viresclient set_default_server https://vires.services/ows
```

### Run for a given time interval

(This runs the CLI provided by SwarmPAL)

Generate a FAC file from Swarm Alpha between two times:

`swarmpal fac-single-sat --spacecraft Swarm-A --grade "FAST" --time_start "2024-03-19" --time_end "2024-03-20" --output "test-A.cdf"`

Check the latest input product availability:

`swarmpal last-available-time "SW_FAST_MAGA_LR_1B"`

### Run as a continuous task

(This runs the processor continuously to generate new FAC files locally as new data is available, and uploads them via FTP)

Configure the FTP server credentials in a `.env` file in the root of `SwarmPAL-processor`:
```
FTP_SERVER="..."
FTP_USERNAME="..."
FTP_PASSWORD="..."
```

Run for a specific satellite:
```
cd tasks
mkdir -p outputs/Sat_A outputs/Sat_B outputs/Sat_C
python fac-fast-processor.py A outputs/Sat_A FAC/TMS/Sat_A
```

(data is stored locally in `./outputs/Sat_A` and uploaded to `FAC/TMS/Sat_A` on the server)

### Run within container (TO DO)

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
