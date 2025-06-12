from dotenv import load_dotenv
import time

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    groq,
    cartesia,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from metrics_logger import MetricsLogger

load_dotenv()

metrics = MetricsLogger()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant named Jarvis.")


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=groq.STT(model="whisper-large-v3-turbo", language="en"),
        llm=groq.LLM(model="llama3-8b-8192"),
        tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    await ctx.connect()
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Timing metrics
    start_time = time.time()
    metrics.mark_event("session_start")

    # Start interaction
    stt_start = time.time()
    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )
    stt_end = time.time()
    metrics.mark_event("EOU", stt_end)

    llm_start = time.time()
    # simulate waiting for first token or capture actual first-token callback
    # ...
    llm_first_token_time = llm_start + 0.5  # mockup
    llm_end = time.time()

    tts_start = time.time()
    # simulate TTS processing
    tts_end = tts_start + 0.7  # mockup

    end_time = time.time()

    # Logging all metrics
    metrics.log_metric("EOU_delay", stt_end - stt_start)
    metrics.log_metric("TTFT", llm_first_token_time - stt_end)
    metrics.log_metric("TTFB", llm_end - stt_end)
    metrics.log_metric("Total_latency", end_time - stt_start)

    # Optional: log usage summary
    metrics.log_summary()

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
