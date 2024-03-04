# provider_video_plutotv
Provides an interface to PlutoTV

Just take the release zip file and drop the provider_video_plutotv folder into the plugins_ext folder. This plugin will normally auto-enable, but most plugins will enable using the following update to the config.ini file
<pre>
[plutotv_default]
label = PlutoTV Instance
</pre>

### NOTES
To get an effective recording, you need to do two things:
1. Use the internalproxy stream type.  This will remove bad DTS/PTS segments.
2. Some channels are not live (like Star Trek). For these channels, each episode has a unique DTS/PTS, which means going across episodes can lead to issues.  Best method is to only record within the episode timeline.  Detailed start and stop times can be adjusted in seconds using the "Start/End Time Adjustment" settings in the instance allowing a near perfect start time.  Video segments are normally around 6 seconds, so you only need to get within that range to hit the beginning of an episode.
