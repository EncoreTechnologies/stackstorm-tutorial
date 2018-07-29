# Convert this into a StackStorm native action

We can do better than simple copy/paste.
Since StackStorm is written in Python there is great support for creating actions
using Python code. 

Some of the benefits of using Python actions in StackStorm:

* python module dependency management (via `requirements.txt`)
* access to a built-in logger
* support for `**kwargs` in `def run()`
* support for native python types (`int`, `bool`, `dict`, `list`)
* automatic conversion of native python types to structured output (`int`, `bool`, `dict`, `list`)
* access to the pack config
* access to the key/value datastore

In this demo we're going to convert the action we just created into a
StackStorm native python action that receives the benefits above.

## Convert the action metadata

First, we need to create an Action Metadata with `runner_type: python-script`. 
This will tell StackStorm we're using a native Python action. It also defines our input
parameters for the action (this will allow us to remove all of our `argparse` code within
the script).

Delete all of the content in the file `/opt/stackstorm/packs/tutorial/actions/nasa_apod.yaml` :

```shell
# hint: delete all of the content in the file
echo "" > /opt/stackstorm/packs/tutorial/actions/nasa_apod.yaml
```

Edit `/opt/stackstorm/packs/tutorial/actions/nasa_apod.yaml` and add the following content:

``` yaml
---
name: nasa_apod
pack: tutorial
description: "Queries NASA's APOD (Astronomy Picture Of the Day) API to get the link to the picture of the day."
runner_type: "python-script"
enabled: true
entry_point: nasa_apod.py
parameters:
  api_key:
    type: string
    description: "API key to use for api.nasa.gov."
    default: "DEMO_KEY"
  hd:
    type: boolean
    description: "Retrieve the high resolution image."
    default: false
  date:
    type: string
    description: "The date [YYYY-MM-DD] of the APOD image to retrieve."
```

You can see in this metadata file that our datatypes are defined along with 
the same defaults and descriptions from the original python script. We're going
to show you how these definitions make the `argparse` code in the python script
no longer necessary!

-----------
**NOTE** 
If you're struggling and just need the answer, simply copy the file from our
answers directory:
```shell
cp /opt/stackstorm/packs/tutorial/etc/answers/actions/nasa_apod_native.yaml /opt/stackstorm/packs/tutorial/actions/nasa_apod.yaml
```
-----------


## Convert the action python

Next, we'll need to convert our Python code over to something compatible
with StackStorm. For native Python actions the following rules need to be met:

* The python script *must* contain a one and only one `class` that inherits from `st2common.runners.base_action.Action`
* The `Action` sub-class *must* define a `def run(self)` function.

Example of the most basic action:

``` yaml
from st2common.runners.base_action import Action


class HelloWorld(Action):

    def run(self):
        return "hello world"
```

For our APOD example we can convert our code by wrapping it in an object and
removing the code in the `if __name__ == "__main__" block (no longer needed):

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
from st2common.runners.base_action import Action


API_URL = "https://api.nasa.gov/planetary/apod"
DEMO_API_KEY = "DEMO_KEY"

class Apod(Action):

    def parse_args(self):
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
    
    def get_apod_metadata(self, args):
        params = {'api_key': args.api_key,
                  'hd': args.hd}
        if args.date is not None:
            params['date'] = args.date
    
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if hd:
            data['url'] = data['hdurl']
        return data
```

We still have a bunch of `argparse` code to pull information from the CLI.
Thanks to StackStorm, we no longer need this code and it can be thrown away.
Instead we'll simply rename our `get_apod_metadata()` function to `run()` 
with the parameters that match the names in the Action Metadata file:
`def run(self, api_key, date, hd):`

The final code in `/opt/stackstorm/packs/tutorial/actions/nasa_apod.py` 
should look like: 

``` python
#!/usr/bin/env python
#
# Description:
#   Queries NASA's APOD (Astronomy Picture Of the Day) API to get the link to the picture
#   of the day.
#
import json
import requests
from st2common.runners.base_action import Action

API_URL = "https://api.nasa.gov/planetary/apod"


class Apod(Action):

    def run(self, api_key, date, hd):
        params = {'api_key': api_key,
                  'hd': hd}
        if date is not None:
            params['date'] = date

        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if hd:
            data['url'] = data['hdurl']
        return data
```

-----------
**NOTE** 
If you're struggling and just need the answer, simply copy the file from our
answers directory:
```shell
cp /opt/stackstorm/packs/tutorial/etc/answers/actions/nasa_apod_native.py /opt/stackstorm/packs/tutorial/actions/nasa_apod.py
```
-----------

Let's register with StackStorm

``` shell
st2ctl reload --register-actions
```

And test!

``` shell
st2 run tutorial.nasa_apod date=2018-07-04
```
