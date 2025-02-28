import asyncio
import websockets
import tkinter as tk
from PIL import Image, ImageTk
import base64
import io
import logging
import cv2
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class VideoClient:
    def __init__(self, root, ws_url):
        self.root = root
        self.ws_url = ws_url
        self.label = tk.Label(root)
        self.label.pack()
        self.root.title("Live Video Stream")
        self.root.geometry("800x600")

        # Video writer setup
        self.frame_width = 800
        self.frame_height = 600
        self.fps = 20  # Frames per second
        self.video_writer = cv2.VideoWriter(
            "saved_video.avi", cv2.VideoWriter_fourcc(*"XVID"), self.fps, (self.frame_width, self.frame_height)
        )

        logging.info("Starting WebSocket connection...")
        asyncio.run(self.start_websocket())

    async def receive_video(self, websocket):
        async for message in websocket:
            try:
                img_data = base64.b64decode(message)
                image = Image.open(io.BytesIO(img_data))
                image = image.resize((self.frame_width, self.frame_height), Image.LANCZOS)

                # Convert PIL image to OpenCV format (BGR)
                frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                # Save frame to video
                self.video_writer.write(frame)

                # Convert image for Tkinter
                image_tk = ImageTk.PhotoImage(image)
                self.label.config(image=image_tk)
                self.label.image = image_tk

            except Exception as e:
                logging.error(f"Error processing image: {e}")

    async def start_websocket(self):
        try:
            async with websockets.connect(self.ws_url) as websocket:
                logging.info(f"Connected to WebSocket server at {self.ws_url}")
                await self.receive_video(websocket)
        except Exception as e:
            logging.error(f"Failed to connect to WebSocket: {e}")

    def close(self):
        """Close video writer when the window is closed."""
        self.video_writer.release()
        logging.info("Video saved as 'saved_video.avi'")

if __name__ == "__main__":
    ws_url = "ws://192.168.31.53:8765/"
    root = tk.Tk()
    client = VideoClient(root, ws_url)

    # Close video writer when exiting
    root.protocol("WM_DELETE_WINDOW", client.close)

    root.mainloop()
