# Event Driven Demo

This demo will setup a pipeline that will listen for messages on specific RabbitMQ queues
words and then post messages into one of two Slack channels depending on the body of
the message.
In order to accomplish this we're going to use the following components:

* Sensor - Will query the RabbitMQ API for message on a specific queue
* Trigger - Events that are emitted from the Sensor when a new message is received on the queue
* Rule - Will match the triggers from the Sensor and invoke an action
* Action - Metadata describing the workflow to execute in order to post to Slack
* Workflow - Series of steps (actions) to determine which channel to post into.
             Then finally post the message into the Slack channel.

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
$ st2 trigger-instance list --trigger rabbitmq.new_message
+--------------------------+----------------+-----------------+-----------+
| id                       | trigger        | occurrence_time | status    |
+--------------------------+----------------+-----------------+-----------+
| 5b5dce8e587be00afa97911f | rabbitmq.new_m | Sun, 29 Jul     | processed |
|                          | essage         | 2018 14:26:22   |           |
|                          |                | UTC             |           |
| 5b5dce8e587be00afa979120 | rabbitmq.new_m | Sun, 29 Jul     | processed |
|                          | essage         | 2018 14:26:22   |           |
|                          |                | UTC             |           |
| 5b5dce8e587be00afa97912b | rabbitmq.new_m | Sun, 29 Jul     | processed |
|                          | essage         | 2018 14:26:22   |           |
|                          |                | UTC             |           |
+--------------------------+----------------+-----------------+-----------+
```

You can view the information contained in the trigger like so:

``` shell
$ st2 trigger-instance get 5b5dce8e587be00afa97912b
+-----------------+-----------------------------+
| Property        | Value                       |
+-----------------+-----------------------------+
| id              | 5b5dce8e587be00afa97912b    |
| trigger         | rabbitmq.new_message        |
| occurrence_time | 2018-07-29T14:26:22.482000Z |
| payload         | {                           |
|                 |     "queue": "demoqueue",   |
|                 |     "body": "test sensor"   |
|                 | }                           |
| status          | processed                   |
+-----------------+-----------------------------+
```

## Configure the Rule

The rule that we're going to write will match the `rabbitmq.new_message` trigger
and invoke an action to post this message to Slack (**note**: the action doesn't exist
yet, but we'll be creating it in the upcoming steps).

Rules live in a pack's `rules/` directory and are defined as YAML metadata files.

Create a new rule file in `/opt/stackstorm/packs/tutorial/rules/post_rabbitmq_to_slack.yaml`:
with following content:

``` yaml
---
name: "post_rabbitmq_to_slack"
description: "Post RabbitMQ message to a Slack channel."
enabled: true

trigger:
  type: "rabbitmq.new_message"
  parameters: {}

action:
  ref: "tutorial.post_rabbitmq_to_slack"
  parameters:
    queue: "{{ trigger.queue }}"
    body: "{{ trigger.body }}"
```

-----------
**NOTE**
If you're struggling and just need the answer, simply copy the file from our
answers directory:
```shell
cp /opt/stackstorm/packs/tutorial/etc/answers/rules/post_rabbitmq_to_slack.yaml /opt/stackstorm/packs/tutorial/rules/post_rabbitmq_to_slack.yaml
```
-----------

Next we'll load the rule into the database so that it begins matching messages.

``` shell
st2ctl reload --register-rules
```

### Test the rule

Publish a RabbitMQ message with either `#pyohio` or `#stackstorm` in the body

```shell
st2 run rabbitmq.publish_message host=127.0.0.1 exchange=demo exchange_type=topic routing_key=demokey message="#pyohio"
```

Check StackStorm to ensure that a trigger was created:

``` shell
$ st2 trigger-instance list --trigger rabbitmq.new_message
+--------------------------+----------------+-----------------+-----------+
| id                       | trigger        | occurrence_time | status    |
+--------------------------+----------------+-----------------+-----------+
| 5b5dce8e587be00afa97911f | rabbitmq.new_m | Sun, 29 Jul     | processed |
|                          | essage         | 2018 14:26:22   |           |
|                          |                | UTC             |           |
| 5b5dce8e587be00afa979120 | rabbitmq.new_m | Sun, 29 Jul     | processed |
|                          | essage         | 2018 14:26:22   |           |
|                          |                | UTC             |           |
| 5b5dce8e587be00afa97912b | rabbitmq.new_m | Sun, 29 Jul     | processed |
|                          | essage         | 2018 14:26:22   |           |
|                          |                | UTC             |           |
| 5b5dd083587be00afa97913a | rabbitmq.new_m | Sun, 29 Jul     | processed |
|                          | essage         | 2018 14:34:43   |           |
|                          |                | UTC             |           |
+--------------------------+----------------+-----------------+-----------+
```

Check StackStorm to ensure that our rule matched our trigger (by type):

``` shell
$ st2 rule-enforcement list --rule tutorial.post_rabbitmq_to_slack
+--------------------------+-------------------------------+--------------------------+--------------+-----------------------------+
| id                       | rule.ref                      | trigger_instance_id      | execution_id | enforced_at                 |
+--------------------------+-------------------------------+--------------------------+--------------+-----------------------------+
| 5b5dd083587be00afa97913c | tutorial.post_rabbitmq_to_sla | 5b5dd083587be00afa97913a |              | 2018-07-29T14:34:43.161928Z |
|                          | ck                            |                          |              |                             |
+--------------------------+-------------------------------+--------------------------+--------------+-----------------------------+
```

Get details about the rule enforcement:

``` shell
$ st2 rule-enforcement get 5b5dd083587be00afa97913c
+---------------------+--------------------------------------------------------+
| Property            | Value                                                  |
+---------------------+--------------------------------------------------------+
| id                  | 5b5dd083587be00afa97913c                               |
| rule.ref            | tutorial.post_rabbitmq_to_slack                        |
| trigger_instance_id | 5b5dd083587be00afa97913a                               |
| execution_id        |                                                        |
| failure_reason      | Action "tutorial.post_rabbitmq_to_slack" doesn't exist |
| enforced_at         | 2018-07-29T14:34:43.161928Z                            |
+---------------------+--------------------------------------------------------+
```

This failed as expected since we haven't created the action yet (our next step).


## Create the Action and Workflow

Our action will be a workflow that receives a RabbitMQ message.
The workflow will examine the body of the message and determine what channel
to post the message in depending on the hashtags used. If `#pyohio` then
the message will be posted in the `#pyohio` Slack channel, if `#stackstorm`
then the message will be posted in the `#stackstorm` channel.

First we will create our action metadata file
`/opt/stackstorm/packs/tutorial/actions/post_rabbitmq_to_slack.yaml` with the
following conent:

``` yaml
---
name: post_rabbitm_to_slack
pack: tutorial
description: "Post a RabbitMQ message to Slack"
runner_type: "mistral-v2"
enabled: true
entry_point: workflows/post_rabbitmq_to_slack.yaml
parameters:
  queue:
    type: string
    description: "Queue the message was received on"
  body:
    type: string
    description: "Body of the message"
```

-----------
**NOTE**
If you're struggling and just need the answer, simply copy the file from our
answers directory:
```shell
cp /opt/stackstorm/packs/tutorial/etc/answers/actions/post_rabbitmq_to_slack.yaml /opt/stackstorm/packs/tutorial/actions/post_rabbitmq_to_slack.yaml
```
-----------

Next we will create our workflow file
`/opt/stackstorm/packs/tutorial/actions/workflows/post_rabbitmq_to_slack.yaml`
with the following content:

``` yaml
version: '2.0'

tutorial.post_rabbitmq_to_slack:
  type: direct
  input:
    - queue
    - body
    
  tasks:
    channel_branch:
      action: std.noop
      publish:
        chat_message: "Received a message on RabbitMQ queue {{ _.queue }}\n {{ _.body }}"
      on-complete:
        - post_to_pyohio: "{{ '#pyohio' in _.body }}"
        - post_to_stackstorm: "{{ '#stackstorm' in _.body }}"
        
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
cp /opt/stackstorm/packs/tutorial/etc/answers/actions/workflows/post_rabbitmq_to_slack.yaml /opt/stackstorm/packs/tutorial/actions/workflows/post_rabbitmq_to_slack.yaml
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

Post another message with either `#pyohio` or `#stackstorm` in the message

```shell
st2 run rabbitmq.publish_message host=127.0.0.1 exchange=demo exchange_type=topic routing_key=demokey message="#pyohio"
```

Check to ensure our action executed:

``` shell
$ st2 rule-enforcement list --rule tutorial.post_rabbitmq_to_slack
+--------------------------+--------------------+---------------------+--------------+--------------------+
| id                       | rule.ref           | trigger_instance_id | execution_id | enforced_at        |
+--------------------------+--------------------+---------------------+--------------+--------------------+
| 5b5dd288587be00afa97914c | tutorial.post_rabb | 5b5dd287587be00afa9 | 5b5dd288587be00afa | 2018-07-29T14:43:1 |
|                          | itmq_to_slack      | 79147               | 97914a             | 9.870669Z          |
+--------------------------+--------------------+---------------------+--------------+--------------------+
```

Check the rule-enforcement

``` shell
$ st2 rule-enforcement get 5b5dd288587be00afa97914c
+---------------------+---------------------------------+
| Property            | Value                           |
+---------------------+---------------------------------+
| id                  | 5b5dd288587be00afa97914c        |
| rule.ref            | tutorial.post_rabbitmq_to_slack |
| trigger_instance_id | 5b5dd287587be00afa979147        |
| execution_id        | 5b5dd288587be00afa97914a        |
| failure_reason      |                                 |
| enforced_at         | 2018-07-29T14:43:19.870669Z     |
+---------------------+---------------------------------+

```

Check the action execution by ID contained in the rule enforcement:

``` shell
$ st2 execution get 5b5dd288587be00afa97914a
id: 5b5dd288587be00afa97914a
action.ref: tutorial.post_rabbitmq_to_slack
parameters: 
  body: '#pyohio'
  queue: demoqueue
status: succeeded (3s elapsed)
result_task: post_to_pyohio
result: 
  channel: '#pyohio'
  extra: null
  message: 'Received a message on RabbitMQ queue demoqueue
 #pyohio'
  user: null
  whisper: false
start_timestamp: Sun, 29 Jul 2018 14:43:19 UTC
end_timestamp: Sun, 29 Jul 2018 14:43:22 UTC
+--------------------------+------------------------+----------------+--------------------+-----------------+
| id                       | status                 | task           | action             | start_timestamp |
+--------------------------+------------------------+----------------+--------------------+-----------------+
| 5b5dd288587be00e2675d6ac | succeeded (1s elapsed) | post_to_pyohio | chatops.post_messa | Sun, 29 Jul     |
|                          |                        |                | ge                 | 2018 14:43:20   |
|                          |                        |                |                    | UTC             |
+--------------------------+------------------------+----------------+--------------------+-----------------+
```
