import configparser
import time

from TM1py import TM1Service

config = configparser.ConfigParser()
# storing the credentials in a file is not recommended for purposes other than testing.
# it's better to setup CAM with SSO or use keyring to store credentials in the windows credential manager. Sample:
# Samples/credentials_best_practice.py
config.read(r'..\config.ini')

cube_source = "Retail"
cube_target = "Retail"

# Establish connection to TM1 Source
with TM1Service(**config['tm1srv01']) as tm1_source:
    # Start Change Tracking
    tm1_source.server.initialize_transaction_log_delta_requests("Cube eq '" + cube_source + "'")

    # Continuous checks
    def job():
        entries = tm1_source.server.execute_transaction_log_delta_request()
        if len(entries) > 0:
            cellset = dict()
            for entry in entries:
                cellset[tuple(entry["Tuple"])] = entry["NewValue"]
            with TM1Service(**config['tm1srv02']) as tm1_target:
                tm1_target.cubes.cells.write_values(cube_target, cellset)


    while True:
        job()
        time.sleep(1)
