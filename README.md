# StackStorm tutorial pack


## Initialization

The first step is to install this pack on the StackStorm host:

``` shell
st2 pack install https://github.com/encoretechnologies/stackstorm-tutorial.git
```

Our code should now be present in: `/opt/stackstorm/packs/tutorial/`


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

## Install twitter pack from exchange

We can install packs from the public [StackStorm exchange](https://exchange.stackstorm.org).

``` shell
st2 pack install twitter
```

### Setup a Twitter app

Visit https://apps.twitter.com and create a new App:

``` shell
name = <yuour name here> StackStorm Tutorial
description = StackStorm tutorial application
website = https://stackstorm.org
```

Agree and click submit!

### Create an access Token

* Within your new application click `Keys and Access Tokens`.
* On the top of the page this will contain your `consumer_key` and `consumer_secret`
* At the bottom of the page, generate a new `Access Token`, thisll will be your `access_token` and `access_token_secret`

### Create the Twitter config in StackStorm

``` shell
cp /opt/stackstorm/packs/twitter/twitter.yaml.example /opt/stackstorm/configs/twitter.yaml
```

Edit `/opt/stackstorm/configs/twitter.yaml` and fill in the value from the `Keys and Access Tokens` page. Example:

``` yaml
---
consumer_key: "qwerty"
consumer_secret: "asdfg"

access_token: "abc-123"
access_token_secret: "456def"

query:
  - "StackStorm"
  - "@Stack_Storm"
count: 30
language: en
```

Now, we'll tell StackStorm to load this configuration into its database:

``` shell
st2ctl reload --register-configs
```

### Test out the Twitter pack

`st2 run twitter.update_status status="Test from StackStorm CLI"`


## Workflows

Workflows allow us to chain actions together, implement conditional logic and branching, and 
turn actions into composable automations.

Workflows are actions too! They simply use a different `runner_type: mistral-v2`.

We'll demonstrate workflows by createing one that retrieves the NASA APOD picture URL
then posts this to Twitter.

### Create workflow action metadata

The workflow action's metadata file is just like any other action metadata file. It
has `runner_type: mistral-v2` and `entry_point` set to the workflow YAML file, relative
to the `actions/` directory.



We also define input parameters for the workflow, just like you would a Python action.

`/opt/stackstorm/packs/tutorial/actions/nasa_apod_twitter_post.yaml`
``` yaml
---
name: nasa_apod_twitter_post
pack: tutorial
description: "Queries NASA's APOD (Astronomy Picture Of the Day) API to get the link to the picture of the day, then posts that link to Twitter"
runner_type: "mistral-v2"
enabled: true
entry_point: workflows/nasa_apod_twitter_post.yaml
parameters:
  extra_message:
    type: string
    default: ''
```

### Create the workflow

StackStorm has several different Workflow engines including 
[ActionChain](https://docs.stackstorm.com/actionchain.html), 
[Mistral](https://docs.stackstorm.com/mistral.html),
and the upcoming [Orchestra](https://github.com/StackStorm/orchestra).
We're going to be using Mistral for this example.


In our workflow we want to call `tutorial.nasa_apod` to retrieve our image URL.
Next we'll post this as a message to twitter using `twitter.update_status`.

**Note** The name of the workflow within the workflow file, **MUST** be the same
as the name of the StackStorm `pack.action`:

`/opt/stackstorm/packs/tutorial/actions/workflows/nasa_apod_twitter_post.yaml`

``` yaml
version: '2.0'

tutorial.nasa_apod_twitter_post:
  type: direct
  input:
    - extra_message

  tasks:
    get_apod_url:
      action: tutorial.nasa_apod
      publish:
        apod_url: "{{ task('get_apod_url').result.result.url }}"
      on-success:
        - post_to_twitter

    post_to_twitter:
      action: twitter.update_status
      input:
        status: "{{ _.extra_message }} {{ _.apod_url }}"
```

### Test

``` shell
st2 run tutorial.nasa_apod_twitter_post extra_message='check out this NASA pic:'
```


# ChatOps Demo

The ChatOps demo will connect a chat bot to Slack. Then we will configure a
new ChatOps command, called an `action alias`, that will execute our action
`tutorial.nasa_apod_twitter_post`.

## Create Slack bot

Our first task will be to connect StackStorm ChatOps to our Slack workspace.
For these steps, we assume that you are a Workspace Admin, if not you'll need
to have your Workspace Admin follow these steps and give you back the API Token
for the bot.

Navigate to "Your Workspace" -> Adminsitrator -> Manage Apps

![chatops_01_slack_apps](/img/chatops_01_slack_apps.png)

In the search box type "Bots" and click on the "Bots" app

![chatops_02_slack_bots](/img/chatops_02_slack_bots.png)

Click on "Add Configuration"

![chatops_03_slack_bots_add_configuration](/img/chatops_03_slack_bots_add_configuration.png)

In the username field, pick a username for your bot then press "Add Integration"

![chatops_04_slack_bots_add_bot](/img/chatops_04_slack_bots_add_bot.png)

Copy down the `API Token` field (1) , we will need this for StackStorm. You can also 
edit the `Full Name` (2) field of the bot, this will be the name displayed. To finish
up, press the `Save Integration` button (3).

![chatops_05_slack_bots_configure](/img/chatops_05_slack_bots_configure.png)

![chatops_06_slack_bots_configure](/img/chatops_06_slack_bots_configure.png)

![chatops_07_slack_bots_configure](/img/chatops_07_slack_bots_configure.png)


## Configure ChatOps

We will now take the `Slack API Token` for the Slack bot and configure StackStorm
ChatOps to connect using this information.

First, let's create a `StackStorm API key` that the ChatOps bot will use to communicate
with the StackStorm API:

``` shell
$ st2 apikey create -m '{"used_by": "st2chatops"}'
+------------+--------------------------------------------------------------+
| Property   | Value                                                        |
+------------+--------------------------------------------------------------+
| id         | 5b4b53e4a814c01b1516050b                                     |
| created_at | 2018-07-15T14:02:12.946531Z                                  |
| enabled    | True                                                         |
| key        | NGExZTJjY2Y5ZWI0MWM3NWFlZGE4YzJiZjcxYWQ0ZjA1YjU2M2E2OGMyMWJi |
|            | YTA5N2Y2NDI0MGM4NWEzYTIzZg                                   |
| metadata   | {                                                            |
|            |     "used_by": "st2chatops"                                  |
|            | }                                                            |
| uid        | api_key:fff87d5b4a3ebc2032814077fe3d95575c971ea0dbd0d599228a |
|            | 4f31a07d726216eac040926d715173ec2317acfef04aca8fe644b0ae07d4 |
|            | b324b3ddf9987ac1                                             |
| user       | st2admin                                                     |
+------------+--------------------------------------------------------------+
```

The `key` parameter in the output is our `StackStorm API key` that we will use 
for ChatOps.

The StackStorm ChatOps config file is `/opt/stackstorm/chatops/st2chatops.env`.

Edit this file and set the following fields:

1. `HUBOT_NAME` = `Full Name` of your bot in Slack
2. `ST2_API_KEY` = Value of your `StackStorm API Key`
3. `HUBOT_SLACK_TOKEN` = Value of your `Slack API Token`

``` shell
export ST2_HOSTNAME="${ST2_HOSTNAME:-localhost}"

#####################################################################
# Hubot settings

# set if you don’t have a valid SSL certificate.
export NODE_TLS_REJECT_UNAUTHORIZED=0

# Hubot port - must be accessible from StackStorm
export EXPRESS_PORT=8081

# Log level
export HUBOT_LOG_LEVEL=debug

# Bot name
export HUBOT_NAME="StackStorm"
export HUBOT_ALIAS='!'

######################################################################
# StackStorm settings

# StackStorm API endpoint.
export ST2_API="${ST2_API:-https://${ST2_HOSTNAME}/api}"

# StackStorm auth endpoint.
# export ST2_AUTH_URL="${ST2_AUTH_URL:-https://${ST2_HOSTNAME}/auth}"

# StackStorm API key
export ST2_API_KEY=NGExZTJjY2Y5ZWI0MWM3NWFlZGE4YzJiZjcxYWQ0ZjA1YjU2M2E2OGMyMWJiYTA5N2Y2NDI0MGM4NWEzYTIzZg

# ST2 credentials. Fill in to use any stackstorm account.
# export ST2_AUTH_USERNAME="${ST2_AUTH_USERNAME:-st2admin}"
# export ST2_AUTH_PASSWORD="${ST2_AUTH_PASSWORD:-testp}"

# Public URL of StackStorm instance: used it to offer links to execution details in a chat.
export ST2_WEBUI_URL=https://${ST2_HOSTNAME}

######################################################################
# Chat service adapter settings

# Uncomment one of the adapter blocks below.
# Currently supported: slack, hipchat, xmpp, yammer, spark, irc, flowdock.
# For using other adapters refer to the "Using an external adapter" doc:
# https://docs.stackstorm.com/chatops/chatops.htm

# Slack settings (https://github.com/slackhq/hubot-slack):
#
export HUBOT_ADAPTER=slack
export HUBOT_SLACK_TOKEN=xoxb-133155492256-xxx-yyyy
# Uncomment the following line to force hubot to exit if disconnected from slack.
export HUBOT_SLACK_EXIT_ON_DISCONNECT=1
```

Restart the StackStorm ChatOps service:

``` shell
systemctl restart st2chatops
```

### Test ChatOps in Slack

Login to Slack and Direct Message the bot with the string `help`. This will
ask the bot for a list of all commands. It should respond with output similar to:

![chatops_08_slack_test](/img/chatops_08_slack_test.png)

You can now invite the bot into channels by either mentioning the bot's name
in a channel, or by running the `/invite` command in a channel.


## Creating an Action Alias

When you type `!help` in a channel with a ChatOps bot, or `help` (no `!`) in a
Direct Message, the bot will respond with a list of commands, known as 
`action aliases`. In short an `action alias` is a way to map a chat message into
a StackStorm action invocation. The message may contain input parameters
that will be forwarded on to the action when it is executed.

Action aliases live in a pack's `aliases/` directory, so for our `tutorial`
pack this would be `/opt/stackstorm/packs/tutorial/aliases`. 

Let's create a new action alias that allows us to invoke our `tutorial.nasa_apod_twitter_post`
action from ChatOps. 

To do this we will create a new metadata file 
`/opt/stackstorm/packs/tutorial/aliases/nasa_apod_twitter_post.yaml` with the
following content:

``` yaml
---
name: "nasa_apod_twitter_post"
pack: "tutorial"
action_ref: "tutorial.nasa_apod_twitter_post"
description: "Posts the NASA Astronomy Picture Of the Day to Twitter"
formats:
    - "nasa apod twitter post {{ status }}"
result:
    format: |
        Received the following output from our mission:
          {{ execution.result }}
```

To register this action alias we'll perform a reload command:

``` shell
st2ctl reload --register-aliases
```

The ChatOps bot polls the StackStorm API periodically for new aliases. If we wait
long enough (2 minutes or 120 seconds) then the alias will be available. Alternatively,
if we want the alias to be available immediately we can simply restart the service:

``` shell
systemctl restart st2chatops
```

### Testing the Action Alias

To invoke the action alias we will simply type the following string in chat:

``` shell
!nasa apod twitter post Hello From ChatOps!!!
```

You should see a set of responses in the channel:

![action_alias_01_demo_response](img/action_alias_01_demo_response.png)

As well as a new post on Twitter!

![action_alias_02_twitter_post](img/action_alias_02_twitter_post.png)


# Event Driven Demo

This demo will setup a pipeline that will listen for tweets that contain specific
words and then post those tweets into one of two Slack channels.
In order to accomplish this we're going to use the following components:

* Sensor - Will query the Twitter API for tweets that contain specific words
* Trigger - Events that are emitted from the Sensor when a tweet contians the words
* Rule - Will match the triggers from the Sensor and invoke an action
* Action - Metadata describing the workflow to execute in order to post to Slack
* Workflow - Series of steps (actions) to determine which channel to post into. 
             Then finally post the tweet into the Slack channel.
             
## Configure the Sensor

We're going to reuse an existing sensor from the `twitter` pack called `twitter.search_sensor`.
This sensor uses information from the `twitter` pack configuration located in:
`/opt/stackstorm/configs/twitter.yaml`. The config file contains a `query` parameter
that is used by the `twitter.stream_sensor` as the words to search for in tweets.


Edit `/opt/stackstorm/configs/twitter.yaml` and enter `#PyOhio` and `#Stack_Storm` as items 
in the `query` parameter:

``` yaml
---
consumer_key: "qwerty"
consumer_secret: "asdfg"

access_token: "abc-123"
access_token_secret: "456def"

query:
  - "#PyOhio"
  - "@Stack_Storm"
count: 30
language: en
```

Next we'll reload the pack's configuration so that the database contains
the new values:

``` shell
st2ctl reload --register-configs
```

Then we'll need to restart the Sensor so it uses the new configuration:

``` shell
systemctl restart st2sensorcontainer
```

### Sensor Testing

Post a new tweet with `#PyOhio` in the body.

Check StackStorm to ensure a new trigger instance was created.

``` shell
$ st2 trigger-instance list --trigger twitter.stream_matched_tweet
+--------------------------+-------------------------+-------------------------+-----------+
| id                       | trigger                 | occurrence_time         | status    |
+--------------------------+-------------------------+-------------------------+-----------+
| 5b4a1dd0a814c06e6e12dd6d | twitter.stream_matched_ | Sat, 14 Jul 2018        | processed |
|                          | tweet                   | 15:59:12 UTC            |           |
+--------------------------+-------------------------+-------------------------+-----------+
```

You can view the information contained in the trigger like so:

``` shell
$ st2 trigger-instance get 5b4a1dd0a814c06e6e12dd6d
+-----------------+--------------------------------------------------------------+
| Property        | Value                                                        |
+-----------------+--------------------------------------------------------------+
| id              | 5b4a1dd0a814c06e6e12dd6d                                     |
| trigger         | twitter.stream_matched_tweet                                 |
| occurrence_time | 2018-07-14T15:59:12.616000Z                                  |
| payload         | {                                                            |
|                 |     "lang": "en",                                            |
|                 |     "url": "https://twitter.com/NickMaludyDemo/status/101816 |
|                 | 3007640231936",                                              |
|                 |     "text": "Hello #NickTest",                               |
|                 |     "created_at": "Sat Jul 14 15:59:12 +0000 2018",          |
|                 |     "place": null,                                           |
|                 |     "user": {                                                |
|                 |         "screen_name": "NickMaludyDemo",                     |
|                 |         "description": null,                                 |
|                 |         "name": "NickMaludyDemo",                            |
|                 |         "location": null                                     |
|                 |     },                                                       |
|                 |     "retweet_count": 0,                                      |
|                 |     "id": 1018163007640231936,                               |
|                 |     "favorite_count": 0                                      |
|                 | }                                                            |
| status          | processed                                                    |
+-----------------+--------------------------------------------------------------+
```

## Configure the Rule

The rule that we're going to write will match the `twitter.stream_matched_tweet` trigger
and invoke an action to post this tweet to Slack (**note**: the action doesn't exist
yet, but we'll be creating it in the upcoming steps).

Rules live in a pack's `rules/` directory and are defined as YAML metadata files.

Create a new rule file in `/opt/stackstorm/packs/tutorial/rules/post_tweet_to_slack.yaml`:
with following content:

``` yaml
---
name: "post_tweet_to_slack"
description: "Post Tweet to a Slack channel."
enabled: true

trigger:
  type: "twitter.stream_matched_tweet"
  parameters: {}

action:
  ref: "tutorial.post_tweet_to_slack"
  parameters:
    message: "{{ trigger.text }}"
    handle: "@{{ trigger.user.screen_name }}"
    date: "{{ trigger.created_at }}"
    url: "{{ trigger.url }}"
```

Next we'll load the rule into the database so that it begins matching tweets.

``` shell
st2ctl reload --register-rules
```

### Test the rule

Post a new tweet with `#PyOhio` in the body.

Check StackStorm to ensure that a trigger was created:

``` shell
$ st2 trigger-instance list --trigger twitter.stream_matched_tweet
+--------------------------+-------------------------+-------------------------+-----------+
| id                       | trigger                 | occurrence_time         | status    |
+--------------------------+-------------------------+-------------------------+-----------+
| 5b4a1dd0a814c06e6e12dd6d | twitter.stream_matched_ | Sat, 14 Jul 2018        | processed |
|                          | tweet                   | 15:59:12 UTC            |           |
| 5b4a25b1a814c06e6e12e09a | twitter.stream_matched_ | Sat, 14 Jul 2018        | processed |
|                          | tweet                   | 16:32:49 UTC            |           |
+--------------------------+-------------------------+-------------------------+-----------+
```

Check StackStorm to ensure that our rule matched our trigger (by type):

``` shell
$ st2 rule-enforcement list --rule tutorial.post_tweet_to_slack
+--------------------------+--------------------+---------------------+--------------+--------------------+
| id                       | rule.ref           | trigger_instance_id | execution_id | enforced_at        |
+--------------------------+--------------------+---------------------+--------------+--------------------+
| 5b4a25b1a814c06e6e12e09c | tutorial.post_twee | 5b4a25b1a814c06e6e1 |              | 2018-07-14T16:32:4 |
|                          | t_to_slack         | 2e09a               |              | 9.570092Z          |
+--------------------------+--------------------+---------------------+--------------+--------------------+
```

Check StackStorm to ensure that our rule matched our trigger (by trigger-instance ID, this will return the same results as above):

``` shell
$ st2 rule-enforcement list --trigger-instance 5b4a25b1a814c06e6e12e09a
+--------------------------+--------------------+---------------------+--------------+--------------------+
| id                       | rule.ref           | trigger_instance_id | execution_id | enforced_at        |
+--------------------------+--------------------+---------------------+--------------+--------------------+
| 5b4a25b1a814c06e6e12e09c | tutorial.post_twee | 5b4a25b1a814c06e6e1 |              | 2018-07-14T16:32:4 |
|                          | t_to_slack         | 2e09a               |              | 9.570092Z          |
+--------------------------+--------------------+---------------------+--------------+--------------------+

```

Get details about the rule enforcement:

``` shell
$ st2 rule-enforcement get 5b4a25b1a814c06e6e12e09c
+---------------------+-----------------------------------------------------+
| Property            | Value                                               |
+---------------------+-----------------------------------------------------+
| id                  | 5b4a25b1a814c06e6e12e09c                            |
| rule.ref            | tutorial.post_tweet_to_slack                        |
| trigger_instance_id | 5b4a25b1a814c06e6e12e09a                            |
| execution_id        |                                                     |
| failure_reason      | Action "tutorial.post_tweet_to_slack" doesn't exist |
| enforced_at         | 2018-07-14T16:32:49.570092Z                         |
+---------------------+-----------------------------------------------------+
```

This failed as expected since we haven't created the action yet (our next step).

## Configure the Action and Workflow

Our action will be a workflow that receives information about a tweet.
The workflow will examine the tweet message and determine what channel
to post the tweet in depending on the hashtags used. If `#PyOhio` then
the tweet will be posted in the `#pyohio` Slack channel, if `@Stack_Storm`
then the tweet will be posted in the `#stackstorm` channel.

First we will create our action metadata file
`/opt/stackstorm/packs/tutorial/actions/post_tweet_to_slack.yaml` with the 
following conent:

``` yaml
---
name: post_tweet_to_slack
pack: tutorial
description: "Post a tweet to Slack"
runner_type: "mistral-v2"
enabled: true
entry_point: workflows/post_tweet_to_slack.yaml
parameters:
  message:
    type: string
    description: "Tweet message body."
  handle:
    type: string
    description: "Twitter handle of the user who tweeted"
  date:
    type: string
    description: "The date+time the tweet was created"
  url:
    type: string
    description: "URL to the tweet"
```

Next we will create our workflow file 
`/opt/stackstorm/packs/tutorial/actions/workflows/post_tweet_to_slack.yaml` 
with the following content:

``` yaml
version: '2.0'

tutorial.post_tweet_to_slack:
  type: direct
  input:
    - message
    - handle
    - date
    - url
    
  tasks:
    channel_branch:
      action: std.noop
      publish:
        chat_message: "{{ _.handle }} tweeted on {{ _.date }}: {{ _.message }} - {{ _.url }}"
      on-complete:
        - post_to_pyohio: "{{ '#PyOhio' in _.message }}"
        - post_to_stackstorm: "{{ '@Stack_Storm' in _.message }}"
        
    post_to_pyohio:
      action: chatops.post_message
      input:
        message: "{{ _.chat_message }}"
        channel: "#pyohio"
        
    post_to_stackstorm:
      action: chatops.post_message
      input:
        message: "{{ _.chat_message }}"
        channel: "#stackstorm"
```

Next we'll tell StackStorm about our action, so that our rule can invoke it:

``` shell
st2ctl reload --register-actions
```

### Testing our Action and Workflow

Post another tweet with either `#PyOhio` or `@Stack_Storm`

Check to ensure our action executed:

``` shell
$ st2 rule-enforcement list --rule tutorial.post_tweet_to_slack
+--------------------------+--------------------+---------------------+--------------------+--------------------+
| id                       | rule.ref           | trigger_instance_id | execution_id       | enforced_at        |
+--------------------------+--------------------+---------------------+--------------------+--------------------+
| 5b4a363ba814c06e6e12e791 | tutorial.post_twee | 5b4a363ba814c06e6e1 | 5b4a363ba814c06e6e | 2018-07-14T17:43:2 |
|                          | t_to_slack         | 2e78d               | 12e790             | 3.401819Z          |
+--------------------------+--------------------+---------------------+--------------------+--------------------+
```

Check the rule-enforcement

``` shell
$ st2 rule-enforcement get 5b4a363ba814c06e6e12e791
+---------------------+------------------------------+
| Property            | Value                        |
+---------------------+------------------------------+
| id                  | 5b4a363ba814c06e6e12e791     |
| rule.ref            | tutorial.post_tweet_to_slack |
| trigger_instance_id | 5b4a363ba814c06e6e12e78d     |
| execution_id        | 5b4a363ba814c06e6e12e790     |
| failure_reason      |                              |
| enforced_at         | 2018-07-14T17:43:23.401819Z  |
+---------------------+------------------------------+
```

Check the action execution (by ID or by type):

``` shell
# By ID
$ st2 execution get 5b4a363ba814c06e6e12e790
id: 5b4a363ba814c06e6e12e790
action.ref: tutorial.post_tweet_to_slack
parameters: 
  date: Sat Jul 14 17:43:22 +0000 2018
  handle: '@NickMaludyDemo'
  message: 'Testing my action and workflow #NickTest #PyOhio'
  url: https://twitter.com/NickMaludyDemo/status/1018189225097940998
status: succeeded (2s elapsed)
start_timestamp: Sat, 14 Jul 2018 17:43:23 UTC
end_timestamp: Sat, 14 Jul 2018 17:43:25 UTC
+--------------------------+------------------------+----------------+--------------------+-----------------+
| id                       | status                 | task           | action             | start_timestamp |
+--------------------------+------------------------+----------------+--------------------+-----------------+
| 5b4a363ca814c06e6b76f763 | succeeded (0s elapsed) | post_to_pyohio | chatops.post_messa | Sat, 14 Jul     |
|                          |                        |                | ge                 | 2018 17:43:24   |
|                          |                        |                |                    | UTC             |
+--------------------------+------------------------+----------------+--------------------+-----------------+


# by Type
$ st2 execution list --action tutorial.post_tweet_to_slack
+----------------------------+-----------------+--------------+------------------------+-----------------+---------------+
| id                         | action.ref      | context.user | status                 | start_timestamp | end_timestamp |
+----------------------------+-----------------+--------------+------------------------+-----------------+---------------+
| + 5b4a363ba814c06e6e12e790 | tutorial.post_t | stanley      | succeeded (2s elapsed) | Sat, 14 Jul     | Sat, 14 Jul   |
|                            | weet_to_slack   |              |                        | 2018 17:43:23   | 2018 17:43:25 |
|                            |                 |              |                        | UTC             | UTC           |
+----------------------------+-----------------+--------------+------------------------+-----------------+---------------+
```

