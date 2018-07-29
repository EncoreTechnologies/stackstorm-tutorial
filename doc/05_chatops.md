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
$ st2 apikey create -k -m '{"used_by": "st2chatops"}'
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


```shell
sudo vi /opt/stackstorm/chatops/st2chatops.env
```

Contents of the file:

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
sudo systemctl restart st2chatops
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
    - "nasa apod twitter post date {{ date }} status {{ status }}"
result:
    format: |
        Received the following output from our mission:
          {{ execution.result }}
```

-----------
**NOTE** 
If you're struggling and just need the answer, simply copy the file from our
answers directory:
```shell
cp /opt/stackstorm/packs/tutorial/etc/answers/aliases/nasa_apod_twitter_post.yaml /opt/stackstorm/packs/tutorial/aliases/nasa_apod_twitter_post.yaml
```
-----------

To register this action alias we'll perform a reload command:

``` shell
st2ctl reload --register-aliases
```

The ChatOps bot polls the StackStorm API periodically for new aliases. If we wait
long enough (2 minutes or 120 seconds) then the alias will be available. Alternatively,
if we want the alias to be available immediately we can simply restart the service:

``` shell
sudo systemctl restart st2chatops
```

### Testing the Action Alias

To invoke the action alias we will simply type the following string in chat:

``` shell
# in a Private Message / Direct Message (DM)
nasa apod twitter post date 2018-07-04 status Hello From ChatOps <your name here>!!!

# if the bot is in a channel, need to make it !nasa
!nasa apod twitter post date 2018-07-04 status Hello From ChatOps <your name here>!!!
```

You should see a set of responses in the channel:

![action_alias_01_demo_response](img/action_alias_01_demo_response.png)

As well as a new post on Twitter!

![action_alias_02_twitter_post](img/action_alias_02_twitter_post.png)

