"""Tracing utilities for agent executions."""
import contextlib
import uuid
from typing import Optional


def gen_trace_id() -> str:
    """Generate a unique trace ID for tracking agent executions.
    
    Returns:
        A unique string ID.
    """
    return str(uuid.uuid4())


@contextlib.contextmanager
def trace(workflow_name: str, trace_id: Optional[str] = None):
    """Context manager for tracing agent executions.
    
    Args:
        workflow_name: Name of the workflow being traced.
        trace_id: Optional trace ID. If not provided, one will be generated.
    """
    trace_id = trace_id or gen_trace_id()
    try:
        # In a real implementation, this would initialize tracing
        print(f"Starting trace '{workflow_name}' with ID {trace_id}")
        yield
    finally:
        # In a real implementation, this would finalize tracing
        print(f"Completed trace '{workflow_name}' with ID {trace_id}") 