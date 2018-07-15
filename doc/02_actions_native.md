## First Action

For our first action we're going to convert an existing python script into a StackStorm action. 
Our existing python script lives in [etc/nasa_apod.py](etc/nasa_apod.py). 
This script queries NASA's Astronomy Picture Of the Day API and retrieves a link to the latest
picture.

### Convert this into a StackStorm action - copy/paste

We can drop this script in with no modifications using the process defined here:

https://docs.stackstorm.com/actions.html#converting-existing-scripts-into-actions

``` shell
# copy our python code
cp /opt/stackstorm/packs/tutorial/etc/nasa_apod.py /opt/stackstorm/packs/tutorial/actions/nasa_apod_copy.py
```

Now we need to create an Action Metadata file that tells StackStorm how to execute
our script. Action metadat files are written in YAML. They provide information to 
StackStorm such as script location, and input parameters. 

Notice the `runner_type: local-shell-script`. This tells StackStorm we're executing
a local script. The `entry_point` parameter is the path (relative to the `actions/` directory)
where the script is located. In our example we're using a Python script, but this
could be a bash script, Go binary, or anything else that's executable.

**create an action metadata**
`/opt/stackstorm/packs/tutorial/actions/nasa_apod_copy.yaml`
``` yaml
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
```

Next we need to tell StackStorm that this action has been created so it can
load it into its database:

``` shell
# tell StackStorm we made a new action
st2ctl reload --register-actions
```

Let's test our action:

``` shell
st2 run tutorial.nasa_apod_copy
```

This _should_ have failed with the following error:

``` shell
.
id: 5b2e9820a814c00645a0a9f5
status: failed
parameters: None
result: 
  failed: true
  return_code: 1
  stderr: "Traceback (most recent call last):
  File "/opt/stackstorm/packs/tutorial/actions/nasa_apod_copy.py", line 9, in <module>
    import requests
ImportError: No module named requests"
  stdout: ''
  succeeded: false
```

To fix this we'll install the `requests` library:

``` shell
pip install requests
```

OK, test our action again!

``` shell
st2 run tutorial.nasa_apod_copy
```

We should see some output like:

``` shell
.
id: 5b2e98cea814c00645a0a9f8
status: succeeded
parameters: None
result: 
  failed: false
  return_code: 0
  stderr: ''
  stdout:
    date: '2018-06-23'
    explanation: Winds on Mars can't actually blow spacecraft over. But in the low gravity, martian winds can loft fine dust particles in planet-wide storms, like the dust storm now raging on the Red Planet. From the martian surface on sol 2082 (June 15), this self-portrait from the Curiosity rover shows the effects of the dust storm, reducing sunlight and visibility at the rover's location in Gale crater. Made with the Mars Hand Lens Imager, its mechanical arm is edited out of the mosaicked images. Curiosity's recent drill site Duluth can be seen on the rock just in front of the rover on the left. The east-northeast Gale crater rim fading into the background is about 30 kilometers away. Curiosity is powered by a radioisotope thermoelectric generator and is expected to be unaffected by the increase in dust at Gale crater. On the other side of Mars, the solar-powered Opportunity rover has ceased its operations due to the even more severe lack of sunlight at its location on the west rim of Endeavour crater.
    hdurl: https://apod.nasa.gov/apod/image/1806/PIA22486CuriositySelf2018dustStorm2048.jpg
    media_type: image
    service_version: v1
    title: Curiosity's Dusty Self
    url: https://apod.nasa.gov/apod/image/1806/PIA22486CuriositySelf2018dustStorm1024.jpg
  succeeded: true
```

Changing one of our arguments on the CLI

``` shell
st2 run tutorial.nasa_apod_copy date=2018-06-22
```

### Convert this into a StackStorm action - native

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

First, we need to create an Action Metadata with `runner_type: python-script`. 
This will tell StackStorm we're using a native Python action. It also defines our input
parameters for the action (this will allow us to remove all of our `argparse` code within
the script).

`/opt/stackstorm/packs/tutorial/actions/nasa_apod.yaml`
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
StackStorm action:

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

Let's register with StackStorm

``` shell
st2ctl reload --register-actions
```

And test!

``` shell
st2 run tutorial.nasa_apod
```
