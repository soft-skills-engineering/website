# Soft Skills Engineering

## Publishing An Episode

One script generates the Jekyll page using info from Trello, uploads the mp3 file to the server, and makes a Github pull request:

```bash
cd scripts
./upload path/to/episode/XXX.mp3
```

* Review the mp3 listed in the Jekyll post by copying/pasting the URL into a browser (it looks like `https://dts.podtrac.com/redirect.mp3/download.softskills.audio/sse-XXX.mp3`). Make sure it's fully uploaded by listening to the very end.
* Merge the pull request, the episode will go live in the feed immediately: http://softskills.audio/feed.xml
* However, subscribers use feedburner (which pulls from the feed link above). Feedburner takes up to 30 minutes to get the newest episode.

## Running the Web Site Locally

```
./dev.sh
```

You may have to do this first to get a more recent version of Ruby:

```
rvm install 2.6.3
rvm --default use 2.6.3
bash --login
bundle install
```

Then, add this to your `~/.bash_profile` to make it permanent:

```
source ~/.rvm/scripts/rvm
```