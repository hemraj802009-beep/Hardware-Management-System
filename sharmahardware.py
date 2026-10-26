"""
Sharma Hardware Website Server Runner.
Entry point that delegates to controllers.server_controller.
"""

from controllers.server_controller import run_server

if __name__ == "__main__":
    run_server()
