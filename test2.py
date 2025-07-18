import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.title("JS event test")

js_code = """
<button onclick="
  window.dispatchEvent(new CustomEvent('streamlit:sendMessage', {
    detail: { type: 'test_event', data: 'hello from button' }
  }));
">Send Event</button>
"""

# Listen for the test event
event_data = streamlit_js_eval(events=["test_event"])

if event_data:
    st.success(f"Received event data: {event_data}")
else:
    st.info("Click the button to send event.")

st.components.v1.html(js_code, height=100)
