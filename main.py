from __future__ import annotations

from typing import Annotated, Literal

import httpx
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse


YAHOO_API_ROOT = "https://fantasysports.yahooapis.com/fantasy/v2"

app = FastAPI(
    title="Yahoo Fantasy Football GPT Bridge",
    version="1.0.0",
    description=(
        "Read-only access to a user's Yahoo Fantasy Football leagues, draft, "
        "teams, matchups, standings, and available players."
    ),
)


def bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Yahoo OAuth bearer token required")
    return authorization.split(" ", 1)[1].strip()


async def yahoo_get(path: str, authorization: str | None) -> JSONResponse:
    token = bearer_token(authorization)
    url = f"{YAHOO_API_ROOT}/{path.lstrip('/')}"
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params={"format": "json"},
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Yahoo API unavailable: {exc}") from exc

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Yahoo authorization expired; reconnect Yahoo")
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail={"message": "Yahoo API request failed", "status": response.status_code},
        )

    return JSONResponse(response.json())


@app.get("/health", operation_id="healthCheck")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/leagues", operation_id="getMyFootballLeagues")
async def leagues(
    authorization: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    return await yahoo_get(
        "users;use_login=1/games;game_codes=nfl/leagues",
        authorization,
    )


@app.get("/league/{league_key}/settings", operation_id="getLeagueSettings")
async def league_settings(
    league_key: str,
    authorization: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    return await yahoo_get(f"league/{league_key}/settings", authorization)


@app.get("/league/{league_key}/standings", operation_id="getLeagueStandings")
async def league_standings(
    league_key: str,
    authorization: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    return await yahoo_get(f"league/{league_key}/standings", authorization)


@app.get("/league/{league_key}/teams", operation_id="getLeagueTeams")
async def league_teams(
    league_key: str,
    authorization: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    return await yahoo_get(f"league/{league_key}/teams", authorization)


@app.get("/league/{league_key}/draft", operation_id="getLeagueDraftResults")
async def league_draft(
    league_key: str,
    authorization: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    return await yahoo_get(f"league/{league_key}/draftresults", authorization)


@app.get("/league/{league_key}/scoreboard", operation_id="getLeagueScoreboard")
async def league_scoreboard(
    league_key: str,
    week: Annotated[int | None, Query(ge=1, le=25)] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    suffix = f";week={week}" if week else ""
    return await yahoo_get(f"league/{league_key}/scoreboard{suffix}", authorization)


@app.get("/league/{league_key}/players", operation_id="getAvailablePlayers")
async def available_players(
    league_key: str,
    position: str | None = None,
    status: Literal["A", "FA", "W"] = "A",
    sort: Literal["AR", "PTS", "OR", "PR"] = "AR",
    start: Annotated[int, Query(ge=0, le=1000)] = 0,
    count: Annotated[int, Query(ge=1, le=25)] = 25,
    authorization: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    filters = [f"status={status}", f"sort={sort}", f"start={start}", f"count={count}"]
    if position:
        filters.append(f"position={position.upper()}")
    return await yahoo_get(f"league/{league_key}/players;" + ";".join(filters), authorization)


@app.get("/team/{team_key}/roster", operation_id="getTeamRoster")
async def team_roster(
    team_key: str,
    week: Annotated[int | None, Query(ge=1, le=25)] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    suffix = f";week={week}" if week else ""
    return await yahoo_get(f"team/{team_key}/roster{suffix}", authorization)


@app.get("/team/{team_key}/matchups", operation_id="getTeamMatchups")
async def team_matchups(
    team_key: str,
    authorization: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    return await yahoo_get(f"team/{team_key}/matchups", authorization)


@app.get("/privacy", include_in_schema=False)
async def privacy() -> dict[str, str]:
    return {
        "privacy": (
            "This private, read-only bridge forwards requests to Yahoo using the "
            "user's OAuth access token. It does not intentionally store tokens or league data."
        )
    }
