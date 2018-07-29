# Event Driven Demo

This demo will setup a pipeline that will listen for tweets that contain specific
words and then post those tweets into one of two Slack channels.
In order to accomplish this we're going to use the following components:

* Sensor - Will query the RabbitMQ API for message on a specific queue
* Trigger - Events that are emitted from the Sensor when a new message is received on the queue
* Rule - Will match the triggers from the Sensor and invoke an action
* Action - Metadata describing the workflow to execute in order to post to Slack
* Workflow - Series of steps (actions) to determine which channel to post into.
             Then finally post the tweet into the Slack channel.

## Configure the Sensor

We're going to reuse an existing sensor from the `rabbitmq` pack called `rabbitmq.queues_sensor`.
This sensor uses information from the `rabbitmq` pack configuration located in:
`/opt/stackstorm/configs/rabbitmq.yaml`. The config file contains a `queues` parameter
that tells `rabbitmq.queues_sensor` what queues to listen for messages on.

Copy `/opt/stackstorm/packs/rabbitmq/rabbitmq.yaml.example` to `/opt/stackstorm/configs/rabbitmq.yaml`:

```yaml
sudo cp /opt/stackstorm/packs/rabbitmq/rabbitmq.yaml.example /opt/stackstorm/configs/rabbitmq.yaml
```

Edit the file, changing `host` to `127.0.0.1` and add the `demoqueue` to the `queues` parameter:

**NOTE** You'll need to edit this file with `sudo /opt/stackstorm/configs/rabbitmq.yaml`

``` yaml
---
sensor_config:
  host: "127.0.0.1"
  username: "guest"
  password: "guest"
  rabbitmq_queue_sensor:
    queues:
      - "demoqueue"
    deserialization_method: "json"
```

-----------
**NOTE**
If you're struggling and just need the answer, simply copy the file from our
answers directory:
```shell
sudo cp /opt/stackstorm/packs/tutorial/etc/answers/configs/rabbitmq.yaml /opt/stackstorm/configs/rabbitmq.yaml
```
-----------

Next we'll reload the pack's configuration so that the database contains
the new values:

``` shell
st2ctl reload --register-configs
```

Then we'll need to restart the Sensor so it uses the new configuration:

``` shell
sudo systemctl restart st2sensorcontainer
```

### Sensor Testing

Publish a new message to RabbitMQ

```shell
st2 run rabbitmq.publish_message host=127.0.0.1 exchange=demo exchange_type=topic routing_key=demokey message="test sensor"
```

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

-----------
**NOTE**
If you're struggling and just need the answer, simply copy the file from our
answers directory:
```shell
cp /opt/stackstorm/packs/tutorial/etc/answers/rules/post_tweet_to_slack.yaml /opt/stackstorm/packs/tutorial/rules/post_tweet_to_slack.yaml
```
-----------

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

-----------
**NOTE**
If you're struggling and just need the answer, simply copy the file from our
answers directory:
```shell
cp /opt/stackstorm/packs/tutorial/etc/answers/actions/post_tweet_to_slack.yaml /opt/stackstorm/packs/tutorial/actions/post_tweet_to_slack.yaml
```
-----------

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

-----------
**NOTE**
If you're struggling and just need the answer, simply copy the file from our
answers directory:
```shell
cp /opt/stackstorm/packs/tutorial/etc/answers/actions/workflows/post_tweet_to_slack.yaml /opt/stackstorm/packs/tutorial/actions/workflows/post_tweet_to_slack.yaml
```
-----------

Next we'll tell StackStorm about our action, so that our rule can invoke it:

``` shell
st2ctl reload --register-actions
```

### Invite your bot to #pyohio and #stackstorm

In Slack, create two new channels and invite your bot!

* `/open #pyohio`
  * `/invite @StackStorm`
* `/open #stackstorm`
  * `/invite @StackStorm`


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
