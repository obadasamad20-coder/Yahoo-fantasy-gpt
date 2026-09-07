# Yahoo Fantasy Football GPT Bridge

This project gives a private Custom GPT read-only access to your Yahoo Fantasy
Football league. It forwards the Yahoo OAuth access token supplied by ChatGPT
to Yahoo's Fantasy Sports API. It does not intentionally store OAuth tokens or
league data.

## What it can read

- Your Yahoo football leagues
- League settings, teams, standings, and scoreboard
- Draft results
- Team rosters and matchups
- Available players and waiver players

It cannot edit a lineup, add/drop a player, or submit a waiver claim.

## 1. Put this project on GitHub

1. Unzip this folder.
2. Create a new **private** repository at https://github.com/new.
3. Upload all the files inside `yahoo-fantasy-gpt` to the repository.

## 2. Deploy it on Render

1. Create or sign in to https://render.com.
2. Select **New +**, then **Blueprint**.
3. Connect the private GitHub repository.
4. Render will detect `render.yaml`. Select **Deploy Blueprint**.
5. When deployment finishes, copy the public URL, such as:
   `https://yahoo-fantasy-gpt.onrender.com`
6. Open `/health` after the URL. You should see `{"status":"ok"}`.

## 3. Create the Custom GPT Action

1. In ChatGPT, open **Explore GPTs**, select **Create**, then **Configure**.
2. Under **Actions**, select **Create new action**.
3. For authentication, choose **OAuth**.
4. Enter:
   - Client ID: from your Yahoo Developer app
   - Client secret: from your Yahoo Developer app
   - Authorization URL: `https://api.login.yahoo.com/oauth2/request_auth`
   - Token URL: `https://api.login.yahoo.com/oauth2/get_token`
   - Token exchange method: **Basic authorization header**
5. If the editor requires a scope, use only the read permission associated with
   Fantasy Sports in your Yahoo app. Do not request write access.
6. ChatGPT displays a callback URL. Copy that exact URL; do not invent one.

## 4. Create the Yahoo Developer app

1. Open https://developer.yahoo.com/apps/ and create an application.
2. Choose **Web Application**.
3. Enable **Fantasy Sports** with **Read** permission only.
4. Paste ChatGPT's exact callback URL into the app's redirect URI field.
5. Save the app, then place its Client ID and Client Secret in the GPT Action's
   OAuth configuration. Never place the secret in this project or a chat.

## 5. Add the action schema

1. Open `openapi.yaml`.
2. Replace `YOUR-RENDER-SERVICE.onrender.com` with your real Render hostname.
3. Paste the entire edited file into the Action schema box.
4. Set the privacy policy URL to your Render URL followed by `/privacy`.
5. Save the action and use its test button. Sign in to Yahoo when prompted.

## 6. Suggested GPT instructions

Paste this into the GPT's Instructions box:

> You are my Yahoo Fantasy Football co-manager. Before giving league-specific
> advice, retrieve league settings, current draft results or roster, and the
> relevant available-player list. Account for full-PPR scoring and roster needs.
> Never claim a player is available without checking. Explain the recommended
> move briefly and list two backup choices. All actions are read-only.

## Useful test prompts

- "Find my Yahoo football league and summarize its scoring settings."
- "Show the latest draft picks and recommend my next three options."
- "Check my roster and rank the five best available running backs."
- "Review this week's matchup and recommend my strongest starting lineup."

## Local test

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs. League endpoints will return 401 locally
unless called with a valid Yahoo OAuth bearer token.

