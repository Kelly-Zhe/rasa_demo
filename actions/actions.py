# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import os
from typing import Dict, Text, Any, List
import logging
import sqlalchemy as sa

from rasa_sdk.interfaces import Action
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import (
    SlotSet,
    EventType,
    ActionExecuted,
    SessionStarted,
    Restarted,
    FollowupAction,
    UserUtteranceReverted,
    AllSlotsReset,
)
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.chatbot_db import create_database, chatbotDB

CHATBOT_NAME = os.environ.get("CHATBOT_NAME", "chatbot")
CHATBOT_URL = os.environ.get("CHATBOTURL", f"sqlite:///{CHATBOT_NAME}.db")
ENGINE = sa.create_engine(CHATBOT_URL)
create_database(ENGINE, CHATBOT_NAME)

chatbot_db = chatbotDB(ENGINE)


logger = logging.getLogger(__name__)

# def get_tuling_response(msg):
#     # 替换成自己的key
#     key = "xxx"
#     api = 'http://www.tuling123.com/openapi/api?key={}&info={}'.format(
#         key, msg)
#     return requests.get(api).json()
NEXT_FORM_NAME = {
    "fetch": "fetch_form",
    "photo": "photo_form",
 
}

FORM_DESCRIPTION = {
    "fetch_form": "拿东西",
    "photo_form": "拍照",
}

class ActionTwoStageFallback(Action):

    def name(self) -> Text:
        return "action_two_stage_fallback"

    def run(self, dispatcher: CollectingDispatcher, tracker:Tracker,
     domain:Dict[Text,Any]) -> List[Dict[Text,Any]]:
        dispatcher.utter_message(template = "utter_ask_rephrase")
        return [UserUtteranceReverted()]

class ActionAffirmationFallback(Action):

    def name(self) -> Text:
        return "action_default_ask_affirmation"

    def run(self, dispatcher: CollectingDispatcher, tracker:Tracker,
     domain:Dict[Text,Any]) -> List[Dict[Text,Any]]:
        dispatcher.utter_message( template ="utter_ask_affirmation")
        return [UserUtteranceReverted()]

class ValidatePhotoForm(FormValidationAction):

    def name(self) -> Text:
        return 'validate_photo_form'

    @staticmethod
    def photo_position_db() -> List[Text]:
        """Database of supported photo position"""

        return ["厨房", "卧室", "客厅", "书房", "厕所", "阳台","储物间"]
    
    async def validate_photo_position(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, any],
        )-> Dict[Text, Any]:
        """Validate photo position value."""
        if isinstance(tracker.get_slot("photo_position"),list):
            value = tracker.get_slot("photo_position")[0]
        if value in self.photo_position_db():
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"photo_position": value}
        else:
            # validation failed, set this slot to None so that the
            # user will be asked for the slot again
            dispatcher.utter_message(text="别瞎说了，这个地方不能拍照！")
            # dispatcher.utter_template("utter_wrong_photo_position", tracker)
            return {"photo_position": None}


class ActionsubmitPhotoForm(Action):

    def name(self) -> Text:
        return 'action_submit_photo_form'

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        slots = {
            "photo_thing": None,
            "photo_position": None,
        }

        Allslots = {
            "photo_thing": None,
            "photo_position": None,
            "fetch_thing":None,
            "fetch_position":None
        }

        for slot_name in slots.keys():
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet('requested_slot', slot_name)]

        if isinstance(tracker.get_slot("photo_thing"),list):
            slots["photo_thing"] = tracker.get_slot("photo_thing")[0]
        else:
        	slots["photo_thing"] = tracker.get_slot("photo_thing")

        if isinstance(tracker.get_slot("photo_position"),list):
            slots["photo_position"] = tracker.get_slot("photo_position")[0]
        else:
        	slots["photo_position"] = tracker.get_slot("photo_position")
        	
        dispatcher.utter_message(text = "photo_thing {}, photo_position {}".format(
            slots["photo_thing"],slots["photo_position"]))
        # All slots are filled.
        slots["photo_thing"] = None
        slots["photo_position"] = None
        return (SlotSet(slot, value) for slot, value in slots.items())

# class ActionsubmitPhotoForm(Action):

#     def name(self) -> Text:
#         return 'action_submit_photo_form'

#     async def run(
#         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     ) -> List[EventType]:
#         slots = {
#             "photo_thing": None,
#             "photo_position": None,
#         }

#         for slot_name in slots.keys():
#             if slots[slot_name] is None:
#                 # The slot is not filled yet. Request the user to fill this slot next.
#                 return [SlotSet('requested_slot', slot_name)]
        
#         if isinstance(tracker.get_slot("photo_thing"),list):
#             slots["photo_thing"] = tracker.get_slot("photo_thing")[0]

#         if isinstance(tracker.get_slot("photo_position"),list):
#             slots["photo_position"] = tracker.get_slot("photo_position")[0]

#         dispatcher.utter_message(text = "photo_thing {}, photo_position {}".format(
#             tracker.get_slot("photo_thing"), tracker.get_slot("photo_position")))
#         # All slots are filled.
#         slots["photo_thing"] = None
#         slots["photo_position"] = None
#         return (SlotSet(slot, value) for slot, value in slots.items())


class ValidateFetchForm(FormValidationAction):

    def name(self) -> Text:
        return 'validate_fetch_form'
    @staticmethod
    def fetch_position_db() -> List[Text]:
        """Database of supported photo position"""

        return ["厨房", "卧室", "客厅", "书房", "厕所", "阳台","储物间"]
    
    async def validate_fetch_position(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, any],
        )-> Dict[Text, Any]:
        """Validate photo position value."""
        if isinstance(tracker.get_slot("fetch_position"),list):
            value = tracker.get_slot("fetch_position")[0]
        if value in self.fetch_position_db():
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"fetch_position": value}
        else:
            # validation failed, set this slot to None so that the
            # user will be asked for the slot again
            dispatcher.utter_message(text="别瞎说了，这个地方不能拿东西！")
            # dispatcher.utter_template("utter_wrong_photo_position", tracker)
            return {"fetch_position": None}

class ActionsubmitFetchForm(Action):

    def name(self) -> Text:
        return 'action_submit_fetch_form'

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        slots = {
            "fetch_thing": None,
            "fetch_position": None,
        }

        for slot_name in slots.keys():
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet('requested_slot', slot_name)]

        if isinstance(tracker.get_slot("fetch_thing"),list):
            slots["fetch_thing"] = tracker.get_slot("fetch_thing")[0]
        else:
        	slots["fetch_thing"] = tracker.get_slot("fetch_thing")

        if isinstance(tracker.get_slot("fetch_position"),list):
            slots["fetch_position"] = tracker.get_slot("fetch_position")[0]
        else:
        	slots["fetch_position"] = tracker.get_slot("fetch_position")

        dispatcher.utter_message(text = "fetch_thing {}, fetch_position {}".format(
            slots["fetch_thing"],slots["fetch_position"]))
        # All slots are filled.
        slots["fetch_thing"] = None
        slots["fetch_position"] = None
        return (SlotSet(slot, value) for slot, value in slots.items())


class ActionSwitchFormsAsk(Action):
    """Asks to switch forms"""

    def name(self) -> Text:
        return "action_switch_forms_ask"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the custom action"""
        active_form_name = tracker.active_form.get("name")
        intent_name = tracker.latest_message["intent"]["name"]
        next_form_name = NEXT_FORM_NAME.get(intent_name)

        if (
            active_form_name not in FORM_DESCRIPTION.keys()
            or next_form_name not in FORM_DESCRIPTION.keys()
        ):
            logger.debug(
                f"Cannot create text for `active_form_name={active_form_name}` & "
                f"`next_form_name={next_form_name}`"
            )
            next_form_name = None
        else:
            text = (
                f"我们还没有完成 {FORM_DESCRIPTION[active_form_name]}  "
                f"你确定想要换到 {FORM_DESCRIPTION[next_form_name]} 吗?"
            )
            buttons = [
                {"payload": "/affirm", "title": "Yes"},
                {"payload": "/deny", "title": "No"},
            ]
            dispatcher.utter_message(text=text, buttons=buttons)
        return [SlotSet("next_form_name", next_form_name)]


class ActionSwitchFormsDeny(Action):
    """Does not switch forms"""

    def name(self) -> Text:
        return "action_switch_forms_deny"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the custom action"""
        active_form_name = tracker.active_form.get("name")

        if active_form_name not in FORM_DESCRIPTION.keys():
            logger.debug(
                f"Cannot create text for `active_form_name={active_form_name}`."
            )
        else:
            text = f"好的，我们继续 {FORM_DESCRIPTION[active_form_name]}吧."
            dispatcher.utter_message(text=text)

        return [SlotSet("next_form_name", None)]


class ActionSwitchFormsAffirm(Action):
    """Switches forms"""

    def name(self) -> Text:
        return "action_switch_forms_affirm"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the custom action"""
        active_form_name = tracker.active_form.get("name")
        next_form_name = tracker.get_slot("next_form_name")

        if (
            active_form_name not in FORM_DESCRIPTION.keys()
            or next_form_name not in FORM_DESCRIPTION.keys()
        ):
            logger.debug(
                f"Cannot create text for `active_form_name={active_form_name}` & "
                f"`next_form_name={next_form_name}`"
            )
        else:
            text = (
                f"太棒了. 我们从 {FORM_DESCRIPTION[active_form_name]} "
                f"转换到 {FORM_DESCRIPTION[next_form_name]}. "
                f"完成后你将有机会返回上一个表单"
            )
            dispatcher.utter_message(text=text)

        return [
            SlotSet("previous_form_name", active_form_name),
            SlotSet("next_form_name", None),
        ]


class ActionSwitchBackAsk(Action):
    """Asks to switch back to previous form"""

    def name(self) -> Text:
        return "action_switch_back_ask"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the custom action"""
        previous_form_name = tracker.get_slot("previous_form_name")

        if previous_form_name not in FORM_DESCRIPTION.keys():
            logger.debug(
                f"Cannot create text for `previous_form_name={previous_form_name}`"
            )
            previous_form_name = None
        else:
            text = (
                f"你想要现在回到 "
                f"{FORM_DESCRIPTION[previous_form_name]} 吗?."
            )
            buttons = [
                {"payload": "/affirm", "title": "Yes"},
                {"payload": "/deny", "title": "No"},
            ]
            dispatcher.utter_message(text=text, buttons=buttons)

        return [SlotSet("previous_form_name", None)]

class ActionSessionId(Action):
    def name(self) ->Text:
        return "action_session_id"
    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        conversation_id = tracker.sender_id
        text = (f"你的对话id是: {conversation_id}")
        dispatcher.utter_message(text=text)

        return []

#     if __name__ == "__main__":
#     conversation_id = secrets.token_urlsafe(16)  # 随机生成会话id
#     messages_url = "http://localhost:5005/conversations/{}/messages".format(conversation_id)  # 发送消息
#     predict_url = "http://localhost:5005/conversations/{}/predict".format(conversation_id)  # 预测下一步动作
#     execute_url = "http://localhost:5005/conversations/{}/execute".format(conversation_id)  # 执行动作
#     action = "action_listen"  # 动作初始化为等待输入
#     while True:
#         if action in ["action_listen", "action_default_fallback", "action_restart"]:
#             # 等待输入
#             text = input("Your input ->  ")
#             post(messages_url, data={"text": text, "sender": "user"})  # 发送消息

#         response = post(predict_url)  # 预测下一步动作
#         action = response["scores"][0]["action"]  # 取出置信度最高的下一步动作

#         response = post(execute_url, data={"name": action})  # 执行动作
#         messages = response["messages"]  # 取出对话信息
#         if messages:
#             print(messages)