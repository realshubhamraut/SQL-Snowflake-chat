# utils/snowchat_ui.py
import streamlit as st

def get_model_url(model: str) -> str:
    if model == "Google Gemini":
        return "Google Gemini (models/gemini-2.0-flash)"
    return model

def message_func(message: str, is_user: bool = False, is_df: bool = False, model: str = "Google Gemini"):
    if is_user:
        st.markdown(f"**User:** {message}")
    elif is_df:
        st.dataframe(message)
    else:
        model_url = get_model_url(model)
        st.markdown(f"**Assistant ({model_url}):** {message}")

# Instead of subclassing BaseCallbackHandler (which may be a Pydantic model),
# we define our callback handler as a plain class.
class StreamlitUICallbackHandler:
    def __init__(self, model: str):
        self.model = model
        self.final_message = ""
    
    def start_loading_message(self):
        st.info("Assistant is typing...")
    
    def on_llm_new_token(self, token: str, **kwargs):
        self.final_message += token
