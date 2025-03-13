from dotenv import load_dotenv
import os

import requests

load_dotenv()

deviceId = os.environ.get("switch")

access_token = os.environ.get("PAT")
headers = {'Authorization': 'Bearer ' + access_token}

URL = f"https://api.smartthings.com/v1/devices/{deviceId}/commands"


def get_commands(component, capability, command, arguments = []):
  commands = {
    "commands": [
      {
        "component": component,
        "capability": capability,
        "command": command,
        "arguments": arguments
      }
    ]
  }

  return commands


def on():
  commands = get_commands("main", "switch", "on")
  requests.post(URL, headers=headers, json=commands)


def off():
  commands = get_commands("main", "switch", "off")
  requests.post(URL, headers=headers, json=commands)
