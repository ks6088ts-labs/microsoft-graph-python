import json
import logging
from os import getenv

import httpx
import typer
from dotenv import load_dotenv

assert load_dotenv(override=True), "Failed to load .env file"
logger = logging.getLogger(__name__)
app = typer.Typer(
    add_completion=False,
)


def set_verbosity(verbose: bool):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)


def _get_teams_messages(
    group_id: str,
    channel_id: str,
    access_token: str,
):
    with httpx.Client() as client:
        response = client.get(
            url=f"https://graph.microsoft.com/beta/teams/{group_id}/channels/{channel_id}/messages",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()

        assert response.status_code == 200, f"Failed to get messages: {response.status_code}"
        logger.debug(
            json.dumps(
                response.json(),
                indent=2,
                ensure_ascii=False,
            )
        )

        # print id, subject, createdDateTime in csv format
        return response.json()["value"]


def _get_replies(
    group_id: str,
    channel_id: str,
    message_id: str,
    access_token: str,
):
    with httpx.Client() as client:
        response = client.get(
            url=f"https://graph.microsoft.com/beta/teams/{group_id}/channels/{channel_id}/messages/{message_id}/replies",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()

        assert response.status_code == 200, f"Failed to get messages: {response.status_code}"
        logger.debug(
            json.dumps(
                response.json(),
                indent=2,
            )
        )

        # get fastest reply timestamp
        return response.json()["value"]


@app.command(
    help="get messages from teams channel",
)
def get_teams_messages(
    group_id: str = getenv("GROUP_ID"),
    channel_id: str = getenv("CHANNEL_ID"),
    access_token: str = getenv("ACCESS_TOKEN"),
    verbose: bool = False,
):
    set_verbosity(verbose)
    logger.debug("collect_teams_messages: group_id=%s, channel_id=%s", group_id, channel_id)

    messages = _get_teams_messages(
        group_id=group_id,
        channel_id=channel_id,
        access_token=access_token,
    )

    print("group_id,channel_id,message_id,subject,createdDateTime")
    for message in messages:
        print(f"{group_id},{channel_id},{message['id']},{message['subject']},{message['createdDateTime']}")
    logger.debug("Total messages: %d", len(messages))


@app.command(
    help="get fastest reply to a message",
)
def get_teams_messages_fastest_reply(
    group_id: str = getenv("GROUP_ID"),
    channel_id: str = getenv("CHANNEL_ID"),
    access_token: str = getenv("ACCESS_TOKEN"),
    message_id: str = getenv("MESSAGE_ID"),
    verbose: bool = False,
):
    set_verbosity(verbose)
    logger.debug(
        "collect_teams_messages_replies: group_id=%s, channel_id=%s, message_id=%s",
        group_id,
        channel_id,
        message_id,
    )

    replies = _get_replies(
        group_id=group_id,
        channel_id=channel_id,
        message_id=message_id,
        access_token=access_token,
    )

    fastest_reply = min(replies, key=lambda x: x["createdDateTime"])

    # print group_id, channel_id, message_id, fastest_reply_createdDateTime in csv format
    print(f"{group_id},{channel_id},{message_id},{fastest_reply['createdDateTime']}")
    logger.debug("Total replies: %d", len(replies))


@app.command(
    help="get elapsed time before reply",
)
def get_elapsed_time_before_reply(
    group_id: str = getenv("GROUP_ID"),
    channel_id: str = getenv("CHANNEL_ID"),
    access_token: str = getenv("ACCESS_TOKEN"),
    verbose: bool = False,
):
    set_verbosity(verbose)
    logger.debug("collect_teams_messages: group_id=%s, channel_id=%s", group_id, channel_id)

    messages = _get_teams_messages(
        group_id=group_id,
        channel_id=channel_id,
        access_token=access_token,
    )

    print("group_id,channel_id,message_id,subject,createdDateTime,fastest_reply_createdDateTime")
    for message in messages:
        replies = _get_replies(
            group_id=group_id,
            channel_id=channel_id,
            message_id=message["id"],
            access_token=access_token,
        )
        try:
            fastest_reply = min(replies, key=lambda x: x["createdDateTime"])
        except Exception:
            fastest_reply = {"createdDateTime": "N/A"}
            # logger.error("Failed to get fastest reply: %s", e)

        print(
            f"{group_id},{channel_id},{message['id']},{message['subject']},{message['createdDateTime']},{fastest_reply['createdDateTime']}"
        )


if __name__ == "__main__":
    app()
