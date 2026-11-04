import os
import time
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ফোনের স্ক্রিনের শেষ ডাটা মেমোরিতে সেভ রাখার জন্য
latest_screenshot = {"image": None, "time": 0}

HTML_VIEWER = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Phone Screen</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0a0b10; color: white; text-align: center; padding: 20px; margin: 0; }
        h2 { color: #00e5ff; text-shadow: 0 0 10px rgba(0,229,255,0.5); }
        .container { max-width: 400px; margin: auto; }
        img { width: 100%; border: 3px solid #00e5ff; border-radius: 15px; box-shadow: 0 0 25px rgba(0, 229, 255, 0.4); margin-top: 20px; display: none; }
        #status { margin-top: 15px; color: #2ea043; font-family: monospace; font-size: 14px; font-weight: bold; }
        .loader { border: 4px solid rgba(0,229,255,0.1); border-top: 4px solid #00e5ff; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h2>📱 Live Screen Viewer</h2>
        <div class="loader" id="loader"></div>
        <div id="status">Connecting to phone...</div>
        <img id="screen" src="" alt="Screen Stream">
    </div>
    
    <script>
        let lastUpdate = 0;

        async function fetchScreen() {
            try {
                let res = await fetch('/get_screen');
                let data = await res.json();
                
                if (data.status === "ok") {
                    if (data.updated > lastUpdate) {
                        document.getElementById("loader").style.display = "none";
                        document.getElementById("screen").src = "data:image/jpeg;base64," + data.image;
                        document.getElementById("screen").style.display = "block";
                        document.getElementById("status").innerText = "✅ Live | Updated: " + new Date().toLocaleTimeString();
                        lastUpdate = data.updated;
                    }
                }
            } catch (e) {
                console.log("Waiting for phone...", e);
            }
        }

        // প্রতি ১ সেকেন্ডে নতুন স্ক্রিনশট চেক করবে
        setInterval(fetchScreen, 1000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_VIEWER)

@app.route('/upload_screen', methods=['POST'])
def upload_screen():
    global latest_screenshot
    try:
        data = request.json
        image_data = data.get('image')
        if image_data:
            latest_screenshot["image"] = image_data
            latest_screenshot["time"] = time.time()
            return jsonify({"status": "ok"}), 200
        return jsonify({"status": "no image"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_screen')
def get_screen():
    global latest_screenshot
    if latest_screenshot["image"]:
        return jsonify({
            "status": "ok", 
            "image": latest_screenshot["image"],
            "updated": latest_screenshot["time"]
        })
    return jsonify({"status": "waiting"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)