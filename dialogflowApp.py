from google.oauth2 import service_account
from google.cloud import dialogflowcx_v3 as dialogflow
import streamlit as st
import uuid
import requests

# 고정값 설정
PROJECT_ID = "lottecard-test"
LOCATION_ID = "global"
SESSION_ID = str(uuid.uuid4())

LANGUAGE_CODE = "ko"
CREDENTIALS = service_account.Credentials.from_service_account_file('./key.json')
client_options = {"api_endpoint": f"{LOCATION_ID}-dialogflow.googleapis.com"}
agent_id = "2b0a77e3-c4f4-497e-9fe4-b2f36555d95f"


# Initialize the Dialogflow session client
session_client = dialogflow.SessionsClient(client_options=client_options, credentials=CREDENTIALS)


def load_css_from_file():
    with open('css/style.css', "r", encoding='utf-8') as f:
        css_content = f.read()
    st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

load_css_from_file() 


def send_to_dialogflow(prompt, agent_id):
    session_path = session_client.session_path(PROJECT_ID, LOCATION_ID, agent_id, str(uuid.uuid4()))
    text_input = dialogflow.TextInput(text=prompt)
    query_input = dialogflow.QueryInput(text=text_input, language_code = 'ko')
    
    # Send the request to Dialogflow
    response = session_client.detect_intent(request={"session": session_path, "query_input": query_input})
    
    # Extract the response message correctly
    parameters = response.query_result.parameters
    
    if parameters == None:
        return response.query_result.response_messages[0].text.text[0]
    elif(parameters.get("$request.generative.DynamicFAQResponse") != None):
        return parameters.get("$request.generative.DynamicFAQResponse")
    else:
        return response.query_result.response_messages[0].text.text[0]


# UI 구성
with st.sidebar:
    st.image('images/gpside-removebg.png')
    if st.button('+'+'새로운 채팅'):
        st.session_state.messages = [{"role": "assistant", "content": "Google Analytics Knowledge base 기반의 Chatbot 서비스 입니다."}]
    # agent_id = st.text_input("Dialogflow Agent ID", key="dialogflow_agent_id")

st.image('images/ga4-removebg.png')
st.title("GoldenPlanet Chatbot")
st.caption("🚀 chatbot powered by Dialogflow CX")
if 'messages' not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Google Analytics Knowledge base 기반의 Chatbot 서비스 입니다."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Streamlit chat input
prompt = st.chat_input()
if prompt:
    if not agent_id:
        st.info("Please add your Agent Id to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Send the user's message to Dialogflow and get the response
    msg = send_to_dialogflow(prompt, agent_id)
    
    if msg:
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant", avatar=st.image('image/gpicon.png')).write(msg)