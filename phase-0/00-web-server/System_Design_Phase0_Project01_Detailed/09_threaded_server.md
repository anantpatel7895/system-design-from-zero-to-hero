
# threaded_server.py

Main Thread:
accept()

Worker Thread:
handle_client()

Advantages:
- Multiple clients concurrently

Problems:
- Memory overhead
- Context switching
- Thousands of threads become expensive
