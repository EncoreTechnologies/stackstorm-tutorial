# Initialization

In this part of the tutorial we're going to login to our StackStorm box, 
authenticate with StackStorm and finally install this tutorial pack.

## Provisioning

If you're doing this at home, you'll need to provision a StackStorm node.
This can be done in a number of different ways detailed in the [StackStorm install docs](https://docs.stackstorm.com/install/index.html).
You can also use [terraform-st2](https://github.com/EncoreTechnologies/terraform-st2)
that was used for the PyOhio 2018 tutorial.

## Login

SSH into your StackStorm host:

```shell
# the hostname should be on the card at your station
ssh ubuntu@ec2-x-x-x-x.us-east-y.compute.amazonaws.com
```

If you're following along at home and logging into a CentOS host instead of
an Ubuntu host you'll want to ssh in as root:

```shell
ssh root@stackstorm.doain.tld
```

## Authenticate

In order to perform actions on the command line and/or API, you need a valid
authentication token. Authenticating on the CLI can be performed like so:

```shell
# use the password on the card at your station
st2 login -w st2admin
```

**NOTE** This will write your password to a local file `~/.st2/config`. This is
         **NOT** recommended for production.

## Install the tutorial pack

Next, we want to install this tutorial on the system so we can use the content
in further sections. Packs are simply git repos and can be installed like so:

```shell
st2 pack install https://github.com/encoretechnologies/stackstorm-tutorial.git
```

Our code should now be present in: `/opt/stackstorm/packs/tutorial/`

```shell
ls -l /opt/stackstorm/packs/tutorial/
```
