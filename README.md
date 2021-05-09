# twitch-stream-saver
Record live streams from twitch.tv and watch later.

Requires python3 and streamlink module.
```
python3 -m pip install streamlink
```

Usage: 
```python3 stream_saver.py <streamer_name_or_url> <quality> \[-w\] \[-r\] \[-c\]```

The first two args are positional.
* -w will check if stream is online every 5 minutes.
* -r (Requires -w to work) will repeat waiting if the stream being recorded ends.
* -c will convert stream to mp4 at the end of recording. (ffmpeg required)

## Features
- Logging to file. eg: LOG_2020-05-08.txt
- Discord webhook notifications for script exceptions.
- Convert from .ts to .mp4 when finished recording.
- Saves recorded stream and logs to working directory.
