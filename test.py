import requests
import json
# webhook = 'https://omdenalc-omdena-ng-lagos-chatbot-model.hf.space/webhooks/rest/webhook'
# webhook = 'https://talha9299-rasa-omdena-demo-model-feature-followup.hf.space/webhooks/rest/webhook'

webhook = 'https://awais-nayyar-azz-rasa-chatbot.hf.space/webhooks/rest/webhook'
# webhook = "http://localhost:5005/webhook"

user_input = "make an encounter"
payload = {"sender": "user", "message": user_input}

# payload = {
#     "sender": "user",
#     "message": user_input,
#     "parse_data": {
#         "intent": {
#             "name": "make_encounter",  # Name of the intent (e.g., make_encounter)
#             "confidence": 1.0  # Confidence score of the intent
#         }
#     }
# }

response = requests.post(webhook, json=payload)
bot_reply = response.json()
# previous_bot_reply = bot_reply
print(bot_reply)
