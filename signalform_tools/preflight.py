# -*- coding: utf-8 -*-
import codecs
import datetime
import json
import os
import re
import time
from typing import Dict
from typing import List
from typing import Tuple

import dateutil.parser
import requests
from signalform_tools.utils import download_tfstate


SFX_ENDPOINT = 'https://stream.signalfx.com/v2/signalflow/preflight?'
SFX_TOKEN = 'XYZ'

# see https://docs.signalfx.com/en/latest/reference/analytics-docs/how-choose-data-resolution.html#data-retention-policies
SFX_RETENTION_DAYS = 8
SFX_TIME_MULT: Dict[str, int] = {
    "m": 60 * 1000,
    "h": 60 * 60 * 1000,
    "d": 24 * 60 * 60 * 1000,
    "w": 7 * 24 * 60 * 60 * 1000,
}


def extract_program_text(filename: str) -> List[str]:
    """If configs passed in are from terraform.tfstate process as json
    else use regex to parse tf_plan
    :param filename: config file to read from
    """
    with open(filename) as conf:
        if filename.endswith('.tfstate'):
            configs = json.loads(conf.read())
            program_text = []
            resources = configs['modules'][0]['resources']
            for resource in resources:
                pattern = re.compile("signalform_detector.*")
                if pattern.match(resource) is not None:
                    program_text.append(resources[resource]['primary']['attributes']['program_text'])
            return program_text
        else:
            configs = conf.read()
            pattern = re.compile('program_text:.+(?:=>)?\s+\"(.+)\"')
            return re.findall(pattern, configs)


def send_to_sfx(program_text: str, start: int, stop: int) -> None:
    """Send a POST request to the preflight API and parse results
    :param program_text: detector config in SignalFlow language
    :param start: start time to query from
    :param stop: stop time to query until
    """
    query_params = f'start={start}&stop={stop}'
    url = SFX_ENDPOINT + query_params
    print(f'Program Text in Detector:\n{program_text}')
    headers = {'Content-Type': 'text/plain', 'X-SF-Token': SFX_TOKEN}
    resp = requests.post(url, headers=headers, data=program_text)
    if resp.status_code != 200:
        print(f'ERROR: Received Response:\n {resp.text}\n')
        return
    display_events(resp.text)


def display_events(text: str) -> None:
    """Display fired and resolved events listed in the SignalFx response"""
    all_events_pattern = re.compile('event:\s+event\ndata: {.*?data: }', re.DOTALL)
    total_fired_alerts = 0
    for elem_match in re.findall(all_events_pattern, text):
        fired_pattern = re.match(r'.*"is"\s*:\s*"anomalous"', elem_match, re.DOTALL)
        removed_pattern = re.match(r'.*"is"\s*:\s*"ok"', elem_match, re.DOTALL)
        timestamp_pattern = re.match(r'.*"timestampMs"\s*:\s*([0-9]+)', elem_match, re.DOTALL)
        if timestamp_pattern is not None:
            # convert alert timestamp in ISO time format (local time)
            timestamp_alert = str(datetime.datetime.fromtimestamp(int(timestamp_pattern.group(1)) // 1000))
            if fired_pattern is not None:
                print(f'\nAlert fired at: {timestamp_alert}')
                total_fired_alerts += 1
            elif removed_pattern is not None:
                print(f'Alert resolved at: {timestamp_alert}')
    print(f'\nExpected total number of triggered alerts: {total_fired_alerts}\n')


def parse_sfx_now(input_time: str) -> int:
    """Parse Signalfx Now into SignalFx API epoch milliseconds
    :raise: ValueError
    """
    if input_time == "Now":
        return int(time.time()) * 1000
    raise ValueError(f"{input_time} is not Now")


def parse_sfx_relative_time(input_time: str) -> int:
    """Parse Signalfx relative time into SignalFx API epoch milliseconds
    :raise: ValueError
    """
    match = re.match(r"-([0-9]+)([a-zA-z])", input_time)
    if match:
        unit = match.group(2)
        if unit in SFX_TIME_MULT:
            delta = int(match.group(1)) * SFX_TIME_MULT[unit]
            return int(time.time()) * 1000 - delta
        allowed = ", ".join(SFX_TIME_MULT.keys())
        print(f'ERROR: SignalFx time syntax accepts only {allowed} time units. Provided: {unit}.')
    raise ValueError(f"{input_time} is not a SignalFx relative time.")


def parse_timestamp(input_time: str) -> int:
    """Parse various timestamp formats into SignalFx API epoch milliseconds
    :raise: ValueError
    """
    ts = int(float(input_time))  # either integer or real UNIX epoch time
    # milliseconds
    if 1e12 < ts < 1e13:
        return round(ts / 1000) * 1000  # round to second
    # seconds
    if 1e9 < ts < 1e10:
        return ts * 1000
    print(f'ERROR: {input_time} is neither in epoch milliseconds or seconds.')
    raise ValueError("{input_time} is not a timestamp")


def parse_date(input_time: str) -> int:
    """Parse various timestamp formats into SignalFx API epoch milliseconds
    :raise: ValueError
    """
    return int(dateutil.parser.parse(input_time).timestamp() * 1000)


def extract_timestamp(input_time: str) -> int:
    "Return timestamp in epoch milliseconds (but rounded to the closest second, as requested by SignalFx) from input time"
    parsers = (parse_sfx_now, parse_sfx_relative_time, parse_timestamp, parse_date)
    for parser in parsers:
        try:
            return parser(input_time)
        except ValueError:
            pass
    print(f'ERROR: unrecognized time format {input_time}. Please use either SignalFx relative time format, a date or a UNIX epoch timestamp in seconds or milliseconds. ABORTING')
    exit(1)


def interpret_interval(args) -> Tuple[int, int]:
    """Parse start and stop timestamp out of input arguments"""
    try:
        parse_sfx_now(args.start)
    except ValueError:
        pass
    else:
        print('ERROR: start time cannot be "Now". ABORTING')
        exit(1)

    start = extract_timestamp(args.start)
    stop = extract_timestamp(args.stop)

    if stop <= start:
        print('ERROR: stop time <= start time. ABORTING')
        exit(1)

    retention_end = int((datetime.datetime.now() - datetime.timedelta(days=SFX_RETENTION_DAYS)).timestamp() * 1000)
    if start < retention_end:
        print(f'WARNING: start time is past the highest resolution data retention period ({SFX_RETENTION_DAYS} days). Fired events may differ from what has actually happened in the past.')

    return start, stop


def preflight_signalform(args):
    if args.file:
        filename = args.file
    elif args.remote:
        try:
            download_tfstate()
        except ValueError:
            print('Error downloading remote state')
            return
        filename = os.getcwd() + "/terraform.tfstate"
    else:
        print('No file found!')
        return

    detectors = extract_program_text(filename)
    start, stop = interpret_interval(args)
    for detector in detectors:
        if args.label in detector or args.label == 'ALL':
            send_to_sfx(codecs.decode(detector, 'unicode_escape'), start, stop)
    try:
        if args.remote:
            os.remove(filename)
    except OSError:
        print('Impossible removing file terraform.tfstate')
