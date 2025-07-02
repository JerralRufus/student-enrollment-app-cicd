# student_enrollment_app/metrics.py
import graphyte
import os

# Get Graphite host from environment variable, default to localhost
GRAPHITE_HOST = os.getenv('GRAPHITE_HOST', 'localhost')

# Initialize the sender
# We use a prefix to organize metrics in Graphite
sender = graphyte.Sender(GRAPHITE_HOST, port=2003, prefix='enrollment_app')

def send_metric(name, value):
    """Sends a metric to Graphite."""
    try:
        sender.send(name, value)
        print(f"Sent metric: {name} with value: {value}")
    except Exception as e:
        # In a real app, you'd log this error properly
        print(f"Error sending metric '{name}': {e}")
