#!/usr/bin/env python3
"""
test_client.py

A simple script to test the NSFW Detection API.

Usage:
    python test_client.py /path/to/image.jpg
    python test_client.py /path/to/image.jpg http://your-server-url.com
"""

import sys
import requests

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_client.py /path/to/image.jpg [server_url]")
        sys.exit(1)

    image_path = sys.argv[1]
    server = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8000"
    url = server.rstrip("/") + "/classify"

    try:
        with open(image_path, "rb") as img_file:
            files = {"file": (image_path, img_file, "image/jpeg")}

            print(f"Sending request to {url} ...")
            response = requests.post(url, files=files, timeout=30)

    except FileNotFoundError:
        print(f"Error: Image file not found — {image_path}")
        return
    except Exception as e:
        print("Error sending request:", e)
        return

    if response.status_code == 200:
        print("\n=== API Response ===")
        print(response.json())
    else:
        print(f"\n❌ Error {response.status_code}:")
        print(response.text)

if __name__ == "__main__":
    main()
