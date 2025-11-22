import os
import json
import time
import random
import logging
from typing import Any, Dict

MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"

class BlueFlameOrchestrator:
    def __init__(self):
        try:
            with open("blueflame_prompts.json", "r") as f:
                self.prompts = json.load(f)
        except Exception:
            self.prompts = {}

    def call(self, prompt_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        tempo = payload.get("bpm")
        if MOCK_MODE:
            # Simulate API latency and return canned structure
            time.sleep(0.3)
            return {
                "prompt": self.prompts.get(prompt_key, {}),
                "tempo": tempo,
                "result": {
                    "url": f"/mock/{prompt_key}.bin",
                    "meta": {"bpm": tempo}
                }
            }
        else:
            # Real integration placeholder; respect BLUEFLAME_API_KEY
            api_key = os.getenv("BLUEFLAME_API_KEY")
            if not api_key:
                raise RuntimeError("BLUEFLAME_API_KEY missing; set env or enable MOCK_MODE=true")
            # Example call stub with retry/backoff
            backoff = 0.5
            for attempt in range(5):
                try:
                    # TODO: Replace with real HTTP call to Blue Flame service
                    raise NotImplementedError
                except Exception as e:
                    if attempt == 4:
                        raise
                    time.sleep(backoff)
                    backoff *= 2

orchestrator = BlueFlameOrchestrator()
