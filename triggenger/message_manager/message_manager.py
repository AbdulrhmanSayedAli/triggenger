from triggenger.message_manager.trigger import Trigger
from triggenger.message_manager.message import Message
from triggenger.message_manager.ai_handler import AIHandler
import json


class MessageManager:
    def __init__(self, trigger: Trigger, ai_handler: AIHandler):
        self.trigger = trigger
        self.ai_handler = ai_handler

    def process_message(self, message: Message):
        try:
            system_message = self.ai_handler.generate_system_message(self.trigger)
            response_str = self.ai_handler.categorize_message(message, system_message)
            response = json.loads(response_str)
            type = int(response["type"])
            if type == 0:
                self.trigger.onMessageNotMatched(message)
                return

            action = self.trigger.actions[type - 1]
            params = response["params"]
            self.trigger.onMessageMatched(message, action, params)
        except Exception as e:
            self.trigger.onMessageError(message, e)
