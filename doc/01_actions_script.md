# Convert exiting Python script into a StackStorm action

For our first action we're going to convert an existing python script into a
StackStorm action. Our existing python script lives in [etc/nasa_apod.py](etc/nasa_apod.py). 
This script queries NASA's Astronomy Picture Of the Day API and retrieves a link to the latest
picture.

## Test existing script

Let's ensure this script works by running it:

```shell 
/opt/stackstorm/packs/tutorial/etc/nasa_apod.py --help
/opt/stackstorm/packs/tutorial/etc/nasa_apod.py --date "2018-07-04"
```

It worked, outputting the URL of the NASA Astronomy Picture Of the Day for July 4th 2018.

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

-----------
**NOTE** 
If you're struggling and just need the answer, simply copy the file from our
answers directory:
```shell
cp /opt/stackstorm/packs/tutorial/etc/answers/actions/nasa_apod_script.yaml /opt/stackstorm/packs/tutorial/actions/nasa_apod.yaml
```
-----------

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
$ st2 run tutorial.nasa_apod date=2018-07-04
.
id: 5b5da49c587be00e2675d5f5
status: succeeded
parameters: 
  date: '2018-07-04'
result: 
  failed: false
  return_code: 0
  stderr: ''
  stdout: https://apod.nasa.gov/apod/image/1807/5D4_4276_crs15launch1024.jpg
  succeeded: true
```

We can also see the API calls made by the CLI by passing in the `--debug` flag:

``` shell
st2 --debug run tutorial.nasa_apod date=2018-07-04
```

Notice all of the `cURL` outputs, this makes it very easy to learn the API and
reproduce what the CLI is doing.

