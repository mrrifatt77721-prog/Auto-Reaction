# Multi Reaction Pro

Mobile-friendly Telegram auto-reaction bot and control panel.

## Hosting environment variables
- `BOT_TOKEN`: token from @BotFather
- `PANEL_PASSWORD`: strong password for panel login
- `FLASK_SECRET`: long random secret for sessions
- `PORT`: set by most hosting providers automatically

## Run
```bash
pip install -r requirements.txt
python main.py
```
Open the hosted web URL on your Android phone, log in, add channels, choose emojis, then enable auto reaction.

## Setup
1. Create a bot through @BotFather.
2. Add the bot as an administrator to each channel and ensure reactions are allowed.
3. Add environment variables in your hosting provider's Secrets/Environment section.
4. Deploy and open the public HTTPS URL.
5. In the panel, add channels as `@publicchannel` or the numeric channel ID, select emojis and enable the bot.

## Important
- Keep the token and panel password secret. Do not commit them to a public repository.
- Only new channel posts are processed; there is no backfill for old posts.
- Selected emojis rotate, one reaction per post, not all selected emojis on every post.
- Telegram API permissions and reaction restrictions apply.
- This uses `getUpdates`; another webhook or polling process using the same bot token may conflict.
- Use persistent storage if the hosting provider resets files between deployments.
