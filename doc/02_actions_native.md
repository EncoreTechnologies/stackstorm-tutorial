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

For our APOD example this basic template will look like:

``` python
import requests
from st2common.runners.base_action import Action

API_URL = "https://api.nasa.gov/planetary/apod"


class Apod(Action):

    def run(self):
```

In our APOD example we had a bunch of `argparse` code to pull information from the CLI.
Thanks to StackStorm, we no longer need this code and it can be thrown away.
Instead we'll simply define our `run()` function with the parameters that match
the names in the Action Metadata file: `def run(self, api_key, date, hd):`

``` python
import requests
from st2common.runners.base_action import Action

API_URL = "https://api.nasa.gov/planetary/apod"


class Apod(Action):

    def run(self, api_key, date, hd):
```

Now we can copy the "meat" of our code over and we end up with a working
StackStorm action. The final code in `/opt/stackstorm/packs/tutorial/actions/nasa_apod.py` 
should look like: 

``` python
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
st2 run tutorial.nasa_apod
```
