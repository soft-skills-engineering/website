# Soft Skills Engineering

## Running Locally
To run the site locally:

```
./dev.sh
```

You may have to do this first to get a more recent version of Ruby:

```
rvm install 2.6.3
rvm --default use 2.3.3
bash --login
bundle install
```

Then, add this to your `~/.bash_profile` to make it permanent:

```
source ~/.rvm/scripts/rvm
```


## Publishing An Episode
Install the dependencies:
```bash
cd scripts
pip3 install -r requirements.txt
```

```bash
cd scripts
./create-pull-request [episode-number]
```

Use the trello helper scripts to generate the body of the PR, the URL, and the title:
```bash
cd scripts
./trello-episode-title [episode-number]
./trello-episode-url [episode-number]
./trello-episode-description [episode-number]
```

Review the PR, then merge when good. That will publish the new page to the site, and push out a new episode to the RSS feed.