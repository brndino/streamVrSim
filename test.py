import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval

st.title("3D Object Selector")

# Initialize session state
if "selected" not in st.session_state:
    st.session_state.selected = ""
if "user_text" not in st.session_state:
    st.session_state.user_text = ""

# A-Frame HTML with clickable objects
components.html(
    """
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://aframe.io/releases/1.4.2/aframe.min.js"></script>
      <style>
        html, body { margin: 0; padding: 0; height: 100%; background: #fff; }
        a-scene { width: 100vw; height: 400px; }
      </style>
      <script>
        AFRAME.registerComponent('clickable', {
          init: function () {
            this.el.addEventListener('click', () => {
              const meshId = this.el.id;
              
              // Reset colors of all clickable objects
              document.querySelectorAll('[clickable]').forEach(el => {
                if (el.id === "box") el.setAttribute('color', '#4CC3D9');
                if (el.id === "sphere") el.setAttribute('color', '#EF2D5E');
              });

              // Highlight clicked object
              this.el.setAttribute('color', '#00FF00');

              // Send clicked object to Streamlit
              window.parent.postMessage(
                { type: "AFRAME_CLICK", object: meshId },
                "*"
              );
            });
          }
        });
      </script>
    </head>
    <body>
      <a-scene embedded>
        <a-box id="box" clickable position="-1 1.5 -3" rotation="0 45 0" color="#4CC3D9"></a-box>
        <a-sphere id="sphere" clickable position="1 1.5 -3" radius="0.5" color="#EF2D5E"></a-sphere>
        <a-camera position="0 1.6 0"><a-cursor></a-cursor></a-camera>
      </a-scene>
    </body>
    </html>
    """,
    height=500,
    scrolling=False,
)

# Listen for postMessage events from iframe (fully live)
clicked = streamlit_js_eval(
    js_expressions="""
    new Promise((resolve) => {
        window.onmessage = (event) => {
            if (event.data && event.data.type === "AFRAME_CLICK") {
                resolve(event.data.object);
            }
        };
    })
    """
)

# Update session state immediately
if clicked:
    st.session_state.selected = clicked
    st.session_state.user_text = ""  # Reset text for new object

# Show the text input
if st.session_state.selected:
    st.success(f"You clicked on: {st.session_state.selected}")
    st.session_state.user_text = st.text_input(
        f"Enter text for {st.session_state.selected}:",
        value=st.session_state.user_text
    )
    if st.session_state.user_text:
        st.write(f"You entered: {st.session_state.user_text}")
else:
    st.info("Click an object in the scene to select it.")
