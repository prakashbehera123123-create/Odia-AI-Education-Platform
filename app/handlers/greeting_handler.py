from __future__ import annotations


class GreetingHandler:
    def handle(self, query: str) -> str:
        if any("\u0b00" <= character <= "\u0b7f" for character in query):
            return "ନମସ୍କାର! ଆପଣ କେଉଁ ପାଠ୍ୟ ବିଷୟରେ ସହାୟତା ଚାହୁଁଛନ୍ତି?"
        return "Hello! What would you like to learn today?"
