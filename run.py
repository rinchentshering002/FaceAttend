import subprocess
import sys
import time
import socket
import threading
import os

import gradio_interface

def wait_for_server(host, port, timeout=30):
    """Wait until the Gradio server is available."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False

def start_gradio():
    """Launch the Gradio camera interface."""
    demo = gradio_interface.build_gradio_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=False
    )

if __name__ == "__main__":
    print("Starting FaceAttend Gradio AI service...")
    
    # Start Gradio in the background
    gradio_thread = threading.Thread(target=start_gradio, daemon=True)
    gradio_thread.start()

    if wait_for_server("127.0.0.1", 7860):
        print("Gradio is running on port 7860.")
    else:
        print("Warning: Gradio did not start within the expected time.")

    print("Starting FaceAttend Informative Website...")
    
    # Launch Streamlit from the root folder
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "streamlit_app.py"
    ])