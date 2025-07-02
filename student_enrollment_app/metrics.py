# student_enrollment_app/metrics.py
import graphyte
import os
import logging # <--- ADD THIS

# Get Graphite host from environment variable, default to localhost
GRAPHITE_HOST = os.getenv('GRAPHITE_HOST', 'localhost')

# Initialize the sender
sender = graphyte.Sender(GRAPHITE_HOST, port=2003, prefix='enrollment_app')

def send_metric(name, value):
    """Sends a metric to Graphite."""
    try:
        sender.send(name, value)
        # CHANGE THIS LINE: from print() to logging.info()
        logging.info(f"Sent metric: {name} with value: {value}")
    except Exception as e:
        # CHANGE THIS LINE: Log errors properly too
        logging.error(f"Error sending metric '{name}': {e}")
