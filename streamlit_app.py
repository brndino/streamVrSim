import streamlit as st
import os
import subprocess
import time
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from threading import Thread
from functools import partial
import ssl

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    daemon_threads = True

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'glb', 'gltf'}
STATIC_PORT = 8000
STATIC_ROOT = 'static'
SERVER_URL = f"http://localhost:{STATIC_PORT}/uploads"
# if https replace with https://localhost:{STATIC_PORT}/uploads

# Make sure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def serve_https():
    handler = partial(CORSRequestHandler, directory=STATIC_ROOT)
    httpd = ThreadedHTTPServer(('localhost', STATIC_PORT), handler)
    httpd.socket = ssl.wrap_socket(httpd.socket,
        keyfile="path/to/key.pem",
        certfile="path/to/cert.pem",
        server_side=True
    )
    print(f"🔐 Serving static files at https://localhost:{STATIC_PORT}")
    httpd.serve_forever()

def start_static_server():
    if not is_port_in_use(STATIC_PORT):
        def serve():
            handler = partial(CORSRequestHandler, directory=STATIC_ROOT)
            server = ThreadedHTTPServer(('localhost', STATIC_PORT), handler)
            print(f"🚀 Serving static files with CORS at http://localhost:{STATIC_PORT}")
            server.serve_forever()
        thread = Thread(target=serve, daemon=True)
        thread.start()
        time.sleep(1)

# 🔥 Start the static server
start_static_server()
#serve_https() # for https must have keyfile and certfile

# 🎈 UI
st.set_page_config(page_title="3D Model Uploader + Viewer", page_icon="📦", layout="wide")
st.sidebar.success('Select any page from here')
st.title("3D Model Uploader + Viewer")
st.write("Upload a `.glb` or `.gltf` file and preview it below using A-Frame.")

uploaded_file = st.file_uploader("Upload a 3D model", type=list(ALLOWED_EXTENSIONS))

if uploaded_file and allowed_file(uploaded_file.name):
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Uploaded `{uploaded_file.name}`")

    # Render using A-Frame
    st.markdown("### Preview:")
    st.components.v1.html(f"""
<!-- A-Frame + Extras -->
<script src="https://aframe.io/releases/1.4.2/aframe.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/donmccurdy/aframe-extras@6.1.1/dist/aframe-extras.min.js"></script>
<script>
AFRAME.registerComponent('wasd-fly-controls', {{
  schema: {{ acceleration: {{ default: 20 }} }},
  init: function () {{
    this.keys = {{}};
    window.addEventListener('keydown', e => this.keys[e.code] = true);
    window.addEventListener('keyup', e => this.keys[e.code] = false);
  }},
  tick: function (time, delta) {{
    const deltaSec = delta / 1000;
    const velocity = this.data.acceleration * deltaSec;
    const rig = this.el.object3D;
    const camera = this.el.querySelector('[camera]')?.object3D || this.el.children[0]?.object3D;
    if (!camera) return;
    const dir = new THREE.Vector3();
    const right = new THREE.Vector3();
    const up = new THREE.Vector3(0, 1, 0);
    camera.getWorldDirection(dir);
    dir.y = 0;
    dir.normalize();
    right.crossVectors(dir, up).normalize();
    if (this.keys['KeyW']) rig.position.addScaledVector(dir, velocity);
    if (this.keys['KeyS']) rig.position.addScaledVector(dir, -velocity);
    if (this.keys['KeyA']) rig.position.addScaledVector(right, -velocity);
    if (this.keys['KeyD']) rig.position.addScaledVector(right, velocity);
    if (this.keys['Space']) rig.position.y += velocity;
    if (this.keys['ShiftLeft'] || this.keys['ShiftRight']) rig.position.y -= velocity;
  }}
}});

AFRAME.registerComponent('forward-click-to-mesh', {{
  init: function () {{
    this.el.addEventListener('model-loaded', () => {{
      this.el.object3D.traverse(child => {{
        if (child.isMesh) {{
          child.el = this.el;
          child.addEventListener('click', e => {{
            this.el.emit('click', e);
          }});
        }}
      }});
    }});
  }}
}});

AFRAME.registerComponent('click-details', {{
  schema: {{
    name: {{ type: 'string' }},
    description: {{ type: 'string', default: 'No description available.' }}
  }},
  init: function () {{
    this.el.addEventListener('click', () => {{
      const infoBox = document.getElementById('infoBox');
      const objectName = document.getElementById('objectName');
      if (infoBox && objectName) {{
        infoBox.style.display = 'block';
        objectName.textContent = `${{this.data.name}}: ${{this.data.description}}`;
      }}

      // Remove highlight from previous
      const highlighted = document.querySelector('[click-details].highlighted');
      if (highlighted && highlighted !== this.el) {{
        highlighted.removeState('highlighted');
        highlighted.getObject3D('mesh')?.traverse(n => {{
          if (n.isMesh && n.material?.emissive) {{
            n.material.emissive.setHex(0x000000);
          }}
        }});
      }}

      // Highlight this
      this.el.addState('highlighted');
      this.el.getObject3D('mesh')?.traverse(n => {{
        if (n.isMesh && n.material?.emissive) {{
          n.material.emissive.setHex(0xffaa00);
        }}
      }});
    }});
  }}
}});
</script>
<style>
  body {{ margin: 0; font-family: Arial; }}
  .upload-box {{
      position: absolute;
      top: 10px;
      left: 10px;
      background: white;
      padding: 10px;
      z-index: 10;
      border-radius: 4px;
      box-shadow: 0 0 10px rgba(0,0,0,0.2);
  }}
</style>

<div id="infoBox" style="
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(0,0,0,0.7);
  color: white;
  padding: 10px 15px;
  border-radius: 5px;
  display: none;
  font-size: 14px;
  z-index: 20;
">
  <strong>Object Info:</strong>
  <p id="objectName">Click an object</p>
</div>

<!-- Scene Viewer -->
<a-scene raycaster="objects: .clickable" cursor="rayOrigin: mouse">
  <a-assets>
    <a-asset-item id="uploadedModel" src="{SERVER_URL}/{uploaded_file.name}"></a-asset-item>
  </a-assets>

  <a-sky color="#EDF2FB"></a-sky>
  <a-plane rotation="-90 0 0" width="20" height="10" color="#7BC8A4"></a-plane>

  <a-light type="ambient" intensity="0.5"></a-light>
  <a-light type="directional" intensity="1" position="2 4 -3"></a-light>

  <a-entity id="my-model"
            gltf-model="#uploadedModel"
            position="0 0 0"
            scale="1 1 1"
            class="clickable">
            forward-click-to-mesh
            click-details="name: Uploaded Model; description: This is your 3D model.">
  </a-entity>

  <a-entity laser-controls="hand: right" raycaster="objects: .clickable" line="color: red"></a-entity>
  <a-entity laser-controls="hand: left" raycaster="objects: .clickable" line="color: red"></a-entity>

  <a-entity id="rig"
            position="0 1.6 4"
            wasd-fly-controls="acceleration: 10">
    <a-entity camera look-controls></a-entity>
  </a-entity>
</a-scene>
<script>
  // Mark meshes as clickable and store original color
  document.querySelector('#my-model').addEventListener('model-loaded', () => {{
    const model = document.querySelector('#my-model').getObject3D('mesh');
    if (!model) return;
    model.traverse(node => {{
      if (node.isMesh) {{
        node.userData.clickable = true;
        node.userData.originalColor = node.material.color.clone();
        if (!node.name) node.name = 'UnnamedObject';
      }}
    }});
  }});

  let lastClickedMesh = null;
  document.querySelector('a-scene').addEventListener('click', evt => {{
    const intersection = evt.detail.intersection;
    if (!intersection || !intersection.object) return;
    const clickedMesh = intersection.object;

    if (!clickedMesh.userData.clickable) return;

    // Reset previous highlight
    if (lastClickedMesh) {{
      lastClickedMesh.material.color.copy(lastClickedMesh.userData.originalColor);
    }}

    // Highlight new mesh
    clickedMesh.material.color.set('#FF4444');

    // Show info box
    const infoBox = document.getElementById('infoBox');
    const objectName = document.getElementById('objectName');
    if (infoBox && objectName) {{
      infoBox.style.display = 'block';
      objectName.textContent = `Name: ${{clickedMesh.name}} | Type: ${{clickedMesh.type}}`;
    }}

    lastClickedMesh = clickedMesh;
  }});
</script>
""", height=600)

elif uploaded_file:
    st.error("Invalid file type. Please upload a .glb or .gltf.")
