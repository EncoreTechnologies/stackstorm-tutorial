# Workflows

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

