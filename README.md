# mipt_algobot
This bot enables stress-testing on "Algorithms and Data Structures" course for MIPT students.

## How to launch

To prepare:
* Clone this repo and change directory to there (e.g. `cd mipt_algobot`)
* Set up environment:  `pipenv install python-telegram-bot`
* Create user (name is important): `sudo useradd -s /bin/bash -d \`pwd\`/mipt_algobot/temp/user -m -G sudo vitek`
* Change ownership of testing folder: `sudo chown -R vitek mipt_algobot/temp/user`

To run:
* Change local environment pythonpath: `export PYTHONPATH=${PYTHONPATH}:\`pwd\``
* Run the bot: `pipenv run python mipt_algobot/bot.py`


by [_Nikita Nikitin_](https://vk.com/flekser_from_sirius), MIPT
