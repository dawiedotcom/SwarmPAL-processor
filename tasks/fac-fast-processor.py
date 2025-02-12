# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: swarmpal-processor
#     language: python
#     name: swarmpal-processor
# ---

# %%
import datetime as dt
import logging
import os
import re
import sched
import sys
import time
from ftplib import FTP

from dotenv import dotenv_values
from swarmpal.express import fac_single_sat
from swarmpal.utils.queries import last_available_time


# %%
def configure_logging(spacecraft="_"):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # Create a handlers with level INFO
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(f"logs/fac-fast-processor_{spacecraft}.log")
    file_handler.setLevel(logging.INFO)
    # Set the format of log messages
    formatter = logging.Formatter("%(asctime)s - %(levelname)s:%(name)s:%(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    # Add the handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger



SCHEDULE = sched.scheduler(time.time, time.sleep)
WAIT_TIME = 900


# %%
def get_latest_evaluated(directory) -> "datetime":
    """Scan local directory to identify latest time in files"""
    dir_contents = os.listdir(directory)
    product_naming = r"SW_(FAST|OPER)_FAC(A|B|C)TMS_2F_(\d{8}T\d{6})_(\d{8}T\d{6})_.{4}\.(cdf|CDF)"
    matched_files = [s for s in dir_contents if re.search(product_naming, s)]
    matches = [re.match(product_naming, filename) for filename in matched_files]
    past_end_times = [match.group(4) for match in matches]
    past_end_times = [dt.datetime.strptime(s, "%Y%m%dT%H%M%S") for s in past_end_times]
    past_end_times.sort()
    try:
        # Add 1 second to convert naming scheme closed bound [a,b] to closed-open [a,b)
        return past_end_times[-1] + dt.timedelta(seconds=1)
    except IndexError:
        raise ValueError("No previous files found")


# %%
def job(swarm_spacecraft="A", starting_time=None, output_directory="outputs", remote_directory=None, wait_time=WAIT_TIME, logger=None):
    collection_mag = f"SW_FAST_MAG{swarm_spacecraft}_LR_1B"
    # Check server for latest time in online products
    logger.info("Checking product availability...")
    t_latest_on_server = last_available_time(collection_mag).replace(microsecond=0)
    logger.info(f"Latest availability for {collection_mag}: {t_latest_on_server}")
    # Check saved files for latest time evaluated
    try:
        t_latest_evaluated = get_latest_evaluated(output_directory)
    except ValueError:
        t_latest_evaluated = starting_time
    logger.info(f"Latest processed time end point: {t_latest_evaluated}")
    # Run if there is new data available
    if t_latest_on_server != t_latest_evaluated:
        t_start = t_latest_evaluated
        t_end = t_latest_on_server
        logger.info(f"Evaluating for time period: {t_start} to {t_end}")
        # Determine the name of the file to write (convert from closed-open [a,b) to closed-closed [a,b]
        t_startend_str = f'{t_start.strftime("%Y%m%dT%H%M%S")}_{(t_end - dt.timedelta(seconds=1)).strftime("%Y%m%dT%H%M%S")}'
        output_name = f"{output_directory}/SW_FAST_FAC{swarm_spacecraft}TMS_2F_{t_startend_str}_XXXX.cdf"
        fac_single_sat(spacecraft=f"Swarm-{swarm_spacecraft}", grade="FAST", time_start=t_start, time_end=t_end, to_cdf_file=output_name)
        # Prepare the next starting time to be the current end time
        t_latest_evaluated = t_end
        logger.info(f"New data saved: {output_name}. Waiting to check again ({wait_time}s)")
        # Upload the file to FTP
        if remote_directory:
            upload_to_ftp(output_name, remote_directory, logger)
        logger.info(f"Waiting to check again ({wait_time}s)")
    else:
        logger.info(f"No new data available. Waiting to check again ({wait_time}s)")

    # Schedule next job run
    SCHEDULE.enter(wait_time, 1, job, (swarm_spacecraft, starting_time, output_directory, remote_directory, wait_time, logger))


# %%
def get_ftp_server_credentials(env_file="../.env"):
    env_vars = dotenv_values(env_file)
    server = env_vars.get("FTP_SERVER")
    username = env_vars.get("FTP_USERNAME")
    password = env_vars.get("FTP_PASSWORD")
    return {"server": server, "username":username, "password":password}


def upload_to_ftp(local_file, remote_directory, logger):
    credentials = get_ftp_server_credentials()
    try:
        ftp = FTP(credentials["server"])
        ftp.login(credentials["username"], credentials["password"])
        ftp.cwd(remote_directory)
        with open(local_file, "rb") as file:
            ftp.storbinary("STOR " + local_file.split('/')[-1], file)
        logger.info(f"Successfully uploaded: {local_file} to remote: {remote_directory}")
    except Exception as e:
        logger.error(f"Failed to upload {local_file} to remote: {remote_directory}\n{e}")
        raise e
    finally:
        ftp.quit()


# %%
def main(spacecraft, output_directory, remote_directory):
    logger = configure_logging(spacecraft=spacecraft)
    logger.info(f"Beginning FAC FAST processor for Swarm {spacecraft}")
    # Begin 3 days ago if output_directory is empty
    t0 = dt.datetime.now().date() - dt.timedelta(days=3)
    SCHEDULE.enter(0, 1, job, (spacecraft, t0, output_directory, remote_directory, WAIT_TIME, logger))
    SCHEDULE.run()


if __name__ == "__main__":
    if "get_ipython" in globals():
        main(spacecraft="A", output_directory="outputs/Sat_A", remote_directory="FAC/TMS/Sat_A")
    else:
        if len(sys.argv) != 4:
            print("Usage: python fac-fast-processor.py <spacecraft-letter> <output-dir> <remote-directory>")
        main(sys.argv[1], sys.argv[2], sys.argv[3])
