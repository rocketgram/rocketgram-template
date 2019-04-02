# Template of bot with RocketGram

This is template repo for using to create and run your first bot with
[RocketGram framework](https://github.com/vd2org/rocketgram).
This also demonstrates how to use the framework.

## Run your first bot

### Prepare environment

First, you need copy `app.env.template` to `app.env` and set `TOKEN`
parameter to token taken from [BotFather](https://t.me/BotFather).
Then you can run bot with one of following method.

### Run with venv

Create new `venv` and install dependencies, then run your first bot:

```bash
python -m pip install -r app/requirements.txt

set -a
source app.env
set +a
python app/engine.py
```

### Run with docker

Run everything with docker:

```bash
docker run --env-file app.env --name rocketgram-template -d --restart unless-stopped rocketgram-template
```

### Run in Heroku

TODO!