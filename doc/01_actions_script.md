# Convert exiting Pythong script into a StackStorm action

For our first action we're going to convert an existing python script into a
StackStorm action. Our existing python script lives in [etc/nasa_apod.py](etc/nasa_apod.py). 
This script queries NASA's Astronomy Picture Of the Day API and retrieves a link to the latest
picture.

## Test existing script

Let's ensure this script works by running it:

```shell 
/opt/stackstorm/packs/tutorial/etc/nasa_apod.py
```

It should have failed with the following error:

```shell
$ /opt/stackstorm/packs/tutorial/etc/nasa_apod.py
Traceback (most recent call last):
  File "/opt/stackstorm/packs/tutorial/etc/nasa_apod.py", line 9, in <module>
    import requests
ImportError: No module named requests
```

To fix this we need to install the `requests` library:

```shell
sudo pip install requests
```

Let's test our action again and ensure that it runs:

```shell
$ /opt/stackstorm/packs/tutorial/etc/nasa_apod.py
https://apod.nasa.gov/apod/image/1807/M57Ring_HubbleGendler_960.jpg
```

This time it worked, outputting the URL of the current NASA Astronomy Picture Of the Day.


## Convert our script

We can drop this script in to StackStorm, with no modifications, using the process
defined here:

https://docs.stackstorm.com/actions.html#converting-existing-scripts-into-actions

Let's copy our script into the actions directory for our tutorial pack:

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
| NOTE |
|-----------|
| If you're struggling and just need the answer, simply copy the file from our answers directory: <br> `cp /opt/stackstorm/packs/tutorial/etc/answers/actions/nasa_apod_script.yaml /opt/stackstorm/packs/tutorial/actions/nasa_apod.yaml` |
|----------|


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

Let's test our action:

``` shell
$ st2 run tutorial.nasa_apod
.
id: 5b4bc3d52d30dd33a2e39d2b
status: succeeded
parameters: None
result: 
  failed: false
  return_code: 0
  stderr: ''
  stdout: https://apod.nasa.gov/apod/image/1807/M57Ring_HubbleGendler_960.jpg
  succeeded: true
```

We can change the date requested on the CLI by adding a parameter to the end of our command:

``` shell
st2 run tutorial.nasa_apod_copy date=2018-06-22
```

We can also see the API calls made by the CLI by passing in the `--debug` flag:

``` shell
st2 --debug run tutorial.nasa_apod_copy date=2018-06-22
```

Notice all of the `cURL` outputs, this makes it very easy to learn the API and
reproduce what the CLI is doing.

