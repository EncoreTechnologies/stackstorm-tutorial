#!/usr/bin/env python
#
# Description:
#   Queries NASA's APOD (Astronomy Picture Of the Day) API to get the link to the picture
#   of the day.
#
import argparse
import json
import requests

API_URL = "https://api.nasa.gov/planetary/apod"
DEMO_API_KEY = "DEMO_KEY"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date',
                        help='The date [YYYY-MM-DD] of the APOD image to retrieve.')
    parser.add_argument('--hd',
                        help='Retrieve the high resolution image.',
                        action='store_true')
    parser.add_argument('-a', '--api-key',
                        help='API key to use for api.nasa.gov.',
                        default=DEMO_API_KEY)
    return parser.parse_args()


def get_apod_metadata(args):
    params = {'api_key': args.api_key,
              'hd': args.hd}
    if args.date is not None:
        params['date'] = args.date

    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    args = parse_args()
    metadata = get_apod_metadata(args)
    print(metadata['hdurl'] if args.hd else metadata['url'])
