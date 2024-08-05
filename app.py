import streamlit as st
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

from agents import content_creator as cc
from agents import evaluator as ev
from agents import user_proxy as up
from config.template import course_template

# setup page title and description
st.set_page_config(page_title="HATTED", page_icon="🤖", layout="wide")

st.markdown("HATTED - Hackathon")


class TrackableManagerAgent(GroupChatManager):
    """
    A custom AssistantAgent that tracks the messages it receives.

    This is done by overriding the `_process_received_message` method.
    """

    def _process_received_message(self, message, sender, silent):
        if sender.name == up.name:
            st.chat_message("user").markdown(message)
        else:
            st.chat_message("assistant").markdown(message)
        return super()._process_received_message(message, sender, silent)


class TrackableUserProxyAgent(UserProxyAgent):
    """
    A custom UserProxyAgent that tracks the messages it receives.

    This is done by overriding the `_process_received_message` method.
    """

    def _process_received_message(self, message, sender, silent):
        st.chat_message("user").markdown(message['content'])
        return super()._process_received_message(message, sender, silent)


# setup sidebar: models to choose from and API key input
with st.sidebar:
    st.header("Model configuration")
    falcon_api_key = st.text_input(
        "Falcon API Key",
        key="planner_api_key",
        type="password"
    )
    model = st.selectbox(
        "Choose model",
        ("falcon-180B-chat", "falcon-40b", "falcon-7b")
    )

# falcon_dict = {
#     "falcon-180B-chat": "tiiuae/falcon-180B-chat",
#     "falcon-40b": "tiiuae/falcon-40b",
#     "falcon-7b": "tiiuae/falcon-7b"
# }

llm_config = {
    "config_list": [
        {
            "model": f"tiiuae/{model}",
            "api_key": falcon_api_key,
            "base_url": "https://api.ai71.ai/v1/",
        },

    ],
    "cache_seed": 42,
}


st.title("Democratising Education Through AI")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": course_template,
            "name": "hatted"
        }
    ]

for msg in st.session_state.messages:
    if msg['name'] == up.name:
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])


if prompt := st.chat_input():

    if not falcon_api_key:
        st.warning("Please enter your API Key")

    else:

        # create a UserProxyAgent instance named "user"
        # human_input_mode is set to "NEVER" to prevent the agent from asking for user input
        user_proxy = UserProxyAgent(
            name=up.name,
            system_message=up.system_message,
            human_input_mode="ALWAYS",
            code_execution_config=False,
        )

        creator = AssistantAgent(
            name=cc.name,
            system_message=cc.system_message,
            llm_config=llm_config
        )

        evaluator = AssistantAgent(
            name=ev.name,
            system_message=ev.system_message,
            llm_config=llm_config,
        )

        groupchat = GroupChat(
            agents=[user_proxy, creator, evaluator],
            messages=st.session_state.messages,
            max_round=10,
            speaker_selection_method='round_robin',
        )

        manager = TrackableManagerAgent(
            groupchat=groupchat,
            llm_config=llm_config
        )

        user_proxy.initiate_chat(
            manager,
            message=prompt,
            clear_history=False
        )

st.stop()
