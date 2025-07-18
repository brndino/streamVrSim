import streamlit as st
import streamlit.components.v1 as components

st.title("3D Object Selector")

params = st.query_params
selected = params.get("selected", [""])[0]

if selected:
    st.success(f"You selected: {selected}")
    if st.button("Continue"):
        st.write(f"Handling logic for: {selected}")
else:
    st.info("Click an object to select.")

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
              const baseUrl = window.location.href.split('?')[0];
              const newUrl = `${baseUrl}?selected=${meshId}`;
              window.location.href = newUrl;
            });
          }
        });
      </script>
    </head>
    <body>
      <a-scene embedded>
        <a-box id="box" clickable position="-1 1.5 -3" rotation="0 45 0" color="#4CC3D9"></a-box>
        <a-sphere id="sphere" clickable position="1 1.5 -3" radius="0.5" color="#EF2D5E"></a-sphere>
        <a-camera position="0 1.6 0"></a-camera>
      </a-scene>
    </body>
    </html>
    """,
    height=500,
    scrolling=False
)
