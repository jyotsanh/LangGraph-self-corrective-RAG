from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.base import BaseCheckpointSaver,empty_checkpoint
# # nodes
def clear_memory(memory: BaseCheckpointSaver, thread_id: str) -> None:
    checkpoint = empty_checkpoint()
    memory.put(
        config={
            "configurable": {
                "thread_id": thread_id
                }
            }, 
        checkpoint=checkpoint, 
        metadata={},
        new_versions="asdjb"
                )