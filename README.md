# Discord Music Bot

A Discord music bot built using Python and the `discord.py` library. It allows users to listen to music directly in their voice channels, queue multiple tracks, and manage playback efficiently.

## Features
- Play music from YouTube.
- Queue system for multiple tracks.
- Pause, resume, and skip tracks.
- Auto-disconnect after a period of inactivity.
- Lightweight and easy to deploy.

## Commands

| Command       | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| `!play [url]` | Play a song from the given YouTube URL or resume the current track.        |
| `!pause`      | Pause the currently playing track.                                         |
| `!resume`     | Resume the currently paused track.                                         |
| `!skip`       | Skip the currently playing track and move to the next one in the queue.    |
| `!queue`      | Display the current music queue.                                           |
| `!clear`      | Clear the entire music queue.                                              |
| `!quit`       | Disconnect the bot from the voice channel.                                 |
| `!help`       | Show a list of all available commands.                                     |

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/discord-music-bot.git
