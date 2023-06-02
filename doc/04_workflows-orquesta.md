# Background:
date: 2023-06-02
   I get a failed result when i execute command "st2ctl reload --register-actions"
   result: "st2common.exceptions.db.StackStormDBObjectNotFoundError: Unable to find RunnerType with name="mistral-v2""
version: "3.8.0"
I realized that there should be a discrepancy between the documentation and the latest version, 
so I tried according to the latest type, and I hope this article can help you

# Workflows
Flowing this post Link: https://docs.stackstorm.com/workflows.html
StackStorm supports two types of workflows - Orquesta and ActionChain.
- Orquesta is a new workflow engine, designed specifically for StackStorm, released in 2019. With Orquesta, you can define simple sequential workflows or complex workflows with forks, joins, and sophisticated data transformation and queries. It has replaced the Mistral workflow engine, and will also replace ActionChains. We recommend you write all new workflows in Orquesta.
Use Orquesta for all new workflows.


Let’s start with a Orquesta workflow named nasa_apod_rabbitmq_publish that retrieves the NASA APOD picture URL
then publish this URL to a RabbitMQ Queue.

We'll demonstrate workflows by creating one that retrieves the NASA APOD picture URL
then publish this URL to a RabbitMQ Queue.

### Create workflow action
Edit `/opt/stackstorm/packs/tutorial/actions/nasa_apod_rabbitmq_publish.yaml` and insert
the following content:

``` yaml
---
name: nasa_apod_rabbitmq_publish
pack: tutorial
description: Queries NASA's APOD (Astronomy Picture Of the Day) API to get the link to the picture of the day, then publishes that link to a RabbitMQ queue
runner_type: orquesta
enabled: true
entry_point: workflows/nasa_apod_rabbitmq_publish.yaml
parameters:
  date:
    type: string
    description: "The date [YYYY-MM-DD] of the APOD image to retrieve."
  message:
    type: string
    description: "Extra message to publish with the URL"
  host:
    type: string
    default: "rabbitmq"
  exchange:
    type: string
    default: "demo"
    description: "Name of the RabbitMQ exchange"
  exchange_type:
    type: string
    default: "topic"
    description: "Type of the RabbitMQ exchange"
  routing_key:
    type: string
    default: "demokey"
    description: "Name of the RabbitMQ routing key"
```

-----------


### Create workflow action metadata

As for the corresponding StackStorm action metadata file for the example above. 
The StackStorm pack for this workflow action is named examples. 
The StackStorm action runner is orquesta. The entry point for the StackStorm action 
is the relative path to the YAML file of the workflow definition.
Let’s save this metadata as 

Edit `/opt/stackstorm/packs/tutorial/actions/nasa_apod_rabbitmq_publish.yaml` and insert
the following content:
```yaml
---
name: nasa_apod_rabbitmq_publish
pack: tutorial
description: Queries NASA's APOD (Astronomy Picture Of the Day) API to get the link to the picture of the day, then publishes that link to a RabbitMQ queue
runner_type: orquesta
enabled: true
entry_point: workflows/nasa_apod_rabbitmq_publish.yaml
parameters:
  date:
    type: string
    description: "The date [YYYY-MM-DD] of the APOD image to retrieve."
  message:
    type: string
    description: "Extra message to publish with the URL"
  host:
    type: string
    default: "rabbitmq"
  exchange:
    type: string
    default: "demo"
    description: "Name of the RabbitMQ exchange"
  exchange_type:
    type: string
    default: "topic"
    description: "Type of the RabbitMQ exchange"
  routing_key:
    type: string
    default: "demokey"
    description: "Name of the RabbitMQ routing key"
```

### To create this action in StackStorm, run the command
```shell
st2 action create /opt/stackstorm/packs/tutorial/actions/nasa_apod_rabbitmq_publish.yaml
```
This will register the workflow as examples.orquesta-sequential in StackStorm. The following is what the output should look like.
```shell
$ st2 action create /opt/stackstorm/packs/tutorial/actions/nasa_apod_rabbitmq_publish.yaml
+---------------+--------------------------------------------------------------+
| Property      | Value                                                        |
+---------------+--------------------------------------------------------------+
| id            | 64795f8148c62a0c928273a1                                     |
| name          | nasa_apod_rabbitmq_publish                                   |
| pack          | tutorial                                                     |
| description   | Queries NASA's APOD (Astronomy Picture Of the Day) API to    |
|               | get the link to the picture of the day, then publishes that  |
|               | link to a RabbitMQ queue                                     |
| enabled       | True                                                         |
| entry_point   | workflows/nasa_apod_rabbitmq_publish.yaml                    |
| metadata_file |                                                              |
| notify        |                                                              |
| output_schema | {                                                            |
|               |     "additionalItems": {},                                   |
|               |     "items": {},                                             |
|               |     "uniqueItems": false,                                    |
|               |     "required": false,                                       |
|               |     "secret": false,                                         |
|               |     "additionalProperties": {},                              |
|               |     "definitions": {},                                       |
|               |     "properties": {},                                        |
|               |     "patternProperties": {},                                 |
|               |     "immutable": false                                       |
|               | }                                                            |
| parameters    | {                                                            |
|               |     "date": {                                                |
|               |         "type": "string",                                    |
|               |         "description": "The date [YYYY-MM-DD] of the APOD    |
|               | image to retrieve."                                          |
|               |     },                                                       |
|               |     "message": {                                             |
|               |         "type": "string",                                    |
|               |         "description": "Extra message to publish with the    |
|               | URL"                                                         |
|               |     },                                                       |
|               |     "host": {                                                |
|               |         "type": "string",                                    |
|               |         "default": "rabbitmq"                                |
|               |     },                                                       |
|               |     "exchange": {                                            |
|               |         "type": "string",                                    |
|               |         "default": "demo",                                   |
|               |         "description": "Name of the RabbitMQ exchange"       |
|               |     },                                                       |
|               |     "exchange_type": {                                       |
|               |         "type": "string",                                    |
|               |         "default": "topic",                                  |
|               |         "description": "Type of the RabbitMQ exchange"       |
|               |     },                                                       |
|               |     "routing_key": {                                         |
|               |         "type": "string",                                    |
|               |         "default": "demokey",                                |
|               |         "description": "Name of the RabbitMQ routing key"    |
|               |     }                                                        |
|               | }                                                            |
| ref           | tutorial.nasa_apod_rabbitmq_publish                          |
| runner_type   | orquesta                                                     |
| tags          |                                                              |
| uid           | action:tutorial:nasa_apod_rabbitmq_publish                   |
+---------------+--------------------------------------------------------------+
```
Check if the action is registered
```shell
$ st2 action list
+-------------------------------------+------------+-------------------------------------------------+
| ref                                 | pack       | description                                     |
+-------------------------------------+------------+-------------------------------------------------+
|                                     |            | day.                                            |
| tutorial.nasa_apod_rabbitmq_publish | tutorial   | Queries NASA's APOD (Astronomy Picture Of the   |
|                                     |            | Day) API to get the link to the picture of the  |
|                                     |            | day, then publishes that link to a RabbitMQ     |
|                                     |            | queue                                           |
+-------------------------------------+------------+-------------------------------------------------+
```

### Test

Before we run the example, let’s run the help command 
st2 run tutorial.nasa_apod_rabbitmq_publish -h to see what input parameters are required.
```shell
$ st2 run tutorial.nasa_apod_rabbitmq_publish -h

Queries NASA's APOD (Astronomy Picture Of the Day) API to get the link
to the picture of the day, then publishes that link to a RabbitMQ
queue

Optional Parameters:
    date
        The date [YYYY-MM-DD] of the APOD image to retrieve.
        Type: string

    exchange
        Name of the RabbitMQ exchange
        Type: string
        Default: demo

    exchange_type
        Type of the RabbitMQ exchange
        Type: string
        Default: topic

    host
        Type: string
        Default: rabbitmq

    message
        Extra message to publish with the URL
        Type: string

    notify
        List of tasks to trigger notifications for.
        Type: array
        Default: []
```

### Execution

Run our action, creating a new message!

```shell
st2 run tutorial.nasa_apod_rabbitmq_publish date="2018-07-04"
```


Read from the queue to see if our message was delivered:
```shell
rabbitmqadmin get queue=demoqueue count=99
```