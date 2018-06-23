# StackStorm tutorial pack


## Initialization

The first step is to download this repository to your StackStorm host:

``` shell
git clone https://github.com/encoretechnologies/stackstorm-tutorial
```

Now we're going to tell StackStorm to install our code:

``` shell
st2 pack install file://`pwd`/stackstorm-tutorial
```

Our code should now be present in: `/opt/stackstorm/packs/tutorial/`


## First Action

For our first action we're goint to convert an existing python script into a StackStorm action. 
Our existing python script lives in [etc/nasa_apod.py](etc/nasa_apod.py). 
This script queries NASA's Astronomy Picture Of the Day API and retrieves a link to the latest
picture.

``` python
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
                        type=bool,
                        default=False)
    parser.add_argument('-a', '--api-key',
                        help='API key to use for api.nasa.gov.',
                        default=DEMO_API_KEY)
    return parser.parse_args()


def get_apod_metadata(args):
    params = {'api_key': args.api_key}
    if args.date is not None:
        params['date'] = args.date
    if args.hd is not None:
        params['hd'] = args.hd

    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    args = parse_args()
    get_apod_metadata(args)
```

### Convert this into a StackStorm action

We can drop this script in with no modifications using the process defined here:

https://docs.stackstorm.com/actions.html#converting-existing-scripts-into-actions

``` shell
# copy our python code
cp /opt/stackstorm/packs/tutorial/etc/nasa_apod.py /opt/stackstorm/packs/tutorial/actions/nasa_apod_copy.py
```

Now we need to create an Action Metadata file that tells StackStorm how to execute
our script. Action metadat files are written in YAML. They provide information to 
StackStorm such as script location, and input parameters.

``` shell
# create an action metadata
cat << "EOF" > /opt/stackstorm/packs/tutorial/actions/nasa_apod_copy.yaml
---
name: nasa_apod_copy
pack: tutorial
description: "copy of etc/nasa_apod.py"
runner_type: "local-shell-script"
enabled: true
entry_point: nasa_apod_copy.py
parameters:
  api_key:
    type: string
  hd:
    type: boolean
  date:
    type: string
EOF
```

Next we need to tell StackStorm that this action has been created so it can
load it into its database:

``` shell
# tell StackStorm we made a new action
st2ctl reload --register-actions
```

Finally, let's test our action:

``` shell
st2 run tutorial.nasa_apod_copy
```



