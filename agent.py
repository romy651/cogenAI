from __future__ import annotations

import logging
from typing import Literal
from dotenv import load_dotenv

from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai

from constant import data

load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("my-worker")
logger.setLevel(logging.INFO)

RoomType = Literal["Career_Conversations", "Performance_Reviews", "Performance_Management"]


async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()

    run_multimodal_agent(ctx, participant)

    logger.info("agent started")


def run_multimodal_agent(ctx: JobContext, participant: rtc.RemoteParticipant):
    logger.info("starting multimodal agent")

    room_type = ctx.room.name.split("-")[0]

    logger.info(f"room type: {room_type}")

    instructions = data[room_type]

    logger.info(f"We have the instructions: {instructions}")


    model = openai.realtime.RealtimeModel(
        instructions=(
            "You need assistance from an expert to help you achieve your goal."
            "Your interface with users will be voice. "
            "You should use short and concise responses, and avoiding usage of unpronouncable punctuation. "
            "You should not answer questions that are not related to your goal."
            f"Short description: {instructions['shortDescription']}"
            f"Long description: {instructions['longDescription']}"
            f"Goal: {instructions['goal']}"
        ),
        modalities=["audio", "text"],
    )
    agent = MultimodalAgent(model=model)
    agent.start(ctx.room, participant)

    session = model.sessions[0]
    session.conversation.item.create(
        llm.ChatMessage(
            role="assistant",
            content="Please begin the interaction with the user in a manner consistent with your instructions. Start presenting yourself and telling the user what you want achieve",
        )
    )
    session.response.create()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
