import time
from dotenv import load_dotenv
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
    # Initialize session components
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

    # Start timing metrics
    session_start = time.time()
    metrics.mark_event("session_start", session_start)

    # STT timing (End of Utterance detection)
    stt_start = time.time()

    # LLM processing start
    llm_start = time.time()

    # Generate reply and capture timing
    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )

    # Capture end of utterance
    stt_end = time.time()
    metrics.mark_event("EOU", stt_end)

    # Simulate or capture actual first token time
    # In real implementation, you'd hook into the LLM's streaming callback
    llm_first_token_time = llm_start + 0.5  # Replace with actual first token callback
    llm_end = time.time()

    # TTS timing
    tts_start = time.time()
    # In real implementation, hook into TTS start/end callbacks
    tts_end = tts_start + 0.7  # Replace with actual TTS timing

    session_end = time.time()

    # Calculate and log all metrics
    eou_delay = stt_end - stt_start
    ttft = llm_first_token_time - stt_end  # Time To First Token
    ttfb = llm_end - stt_end               # Time To Full Buffer
    total_latency = session_end - stt_start

    # Log metrics
    metrics.log_metric("EOU_delay", eou_delay)
    metrics.log_metric("TTFT", ttft)
    metrics.log_metric("TTFB", ttfb)
    metrics.log_metric("Total_latency", total_latency)
    metrics.log_metric("TTS_duration", tts_end - tts_start)
    metrics.log_metric("Session_duration", session_end - session_start)

    # Save metrics to Excel file
    metrics.save_to_excel()

    # Optional: log summary to console
    metrics.log_summary()


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
