
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
