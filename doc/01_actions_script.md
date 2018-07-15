# Convert exiting Pythong script into a StackStorm action

For our first action we're going to convert an existing python script into a
StackStorm action. Our existing python script lives in [etc/nasa_apod.py](etc/nasa_apod.py). 
This script queries NASA's Astronomy Picture Of the Day API and retrieves a link to the latest
picture.

We can drop this script in with no modifications using the process defined here:

https://docs.stackstorm.com/actions.html#converting-existing-scripts-into-actions

``` shell
# copy our python code
cp /opt/stackstorm/packs/tutorial/etc/nasa_apod.py /opt/stackstorm/packs/tutorial/actions/nasa_apod.py
```

Now we need to create an Action Metadata file that tells StackStorm how to execute
our script. Action metadat files are written in YAML. They provide information to 
StackStorm such as script location, and input parameters. 

Create an action metadata file `/opt/stackstorm/packs/tutorial/actions/nasa_apod.yaml`
with the following content:

``` yaml
---
name: nasa_apod
pack: tutorial
description: "copy of etc/nasa_apod.py"
runner_type: "local-shell-script"
enabled: true
entry_point: nasa_apod.py
parameters:
  api_key:
    type: string
  hd:
    type: boolean
  date:
    type: string
```

---
**NOTE** 

If you're struggling and just need the answer, simply copy the file from our
answers directory:

```shell
cp /opt/stackstorm/packs/tutorial/etc/answers/actions/nasa_apod_script.yaml /opt/stackstorm/packs/tutorial/actions/nasa_apod.yaml
```
---


Notice the `runner_type: local-shell-script`. This tells StackStorm we're executing
a local script. The `entry_point` parameter is the path (relative to the `actions/` directory)
where the script is located. In our example we're using a Python script, but this
could be a bash script, Go binary, or anything else that's executable.

Next we need to tell StackStorm that this action has been created so it can
load it into its database:

``` shell
# tell StackStorm we made a new action
st2ctl reload --register-actions
```

Let's test our action (this _should_ fail with the following error:

``` shell
$ st2 run tutorial.nasa_apod
.
id: 5b2e9820a814c00645a0a9f5
status: failed
parameters: None
result: 
  failed: true
  return_code: 1
  stderr: "Traceback (most recent call last):
  File "/opt/stackstorm/packs/tutorial/actions/nasa_apod.py", line 9, in <module>
    import requests
ImportError: No module named requests"
  stdout: ''
  succeeded: false
```

To fix this we'll install the `requests` library:

``` shell
pip install requests
```

OK, test our action again (success this time):

``` shell
$ st2 run tutorial.nasa_apod
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
