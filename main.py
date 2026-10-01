import os
import shutil
import tempfile
from flask import Flask, request, render_template_string
from log_parser_body import extract_passwords_racoon, extract_passwords_redline
from cc_parser import process_cc, process_cc_v2

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Stealer Log Parser</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; background-color: #0f172a; color: #f8fafc; }
        .card { background: #1e293b; padding: 24px; border-radius: 12px; max-width: 800px; margin: auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }
        h2 { margin-top: 0; color: #38bdf8; }
        .upload-box { border: 2px dashed #475569; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }
        input[type="file"] { margin-bottom: 15px; }
        button { background-color: #0284c7; color: white; border: none; padding: 12px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; }
        button:hover { background-color: #0369a1; }
        pre { background: #0f172a; padding: 15px; border-radius: 6px; overflow-x: auto; color: #22c55e; border: 1px solid #334155; max-height: 400px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Stealer Malware Log Parser</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <div class="upload-box">
                <label><b>Select Unpacked Log Files/Folders:</b></label><br><br>
                <input type="file" name="files" multiple required><br>
                <button type="submit">Upload & Extract Logs</button>
            </div>
        </form>

        {% if completed %}
        <hr style="border-color: #334155; margin: 25px 0;">
        <h3>Racoon Output</h3>
        <pre>{{ racoon if racoon else 'No entries found.' }}</pre>
        <h3>Redline Output</h3>
        <pre>{{ redline if redline else 'No entries found.' }}</pre>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE, completed=False)

@app.route("/upload", methods=["POST"])
def upload_files():
    uploaded_files = request.files.getlist("files")
    if not uploaded_files:
        return "No files uploaded", 400

    temp_dir = tempfile.mkdtemp()

    try:
        # Save uploaded log files to isolated temp directory
        for file in uploaded_files:
            file_path = os.path.join(temp_dir, file.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)

        output_file = os.path.join(temp_dir, "Treated_passwords_racoon.txt")
        output_file2 = os.path.join(temp_dir, "Treated_passwords_redline.txt")

        # Run parser modules
        process_cc(temp_dir)
        process_cc_v2(temp_dir)
        extract_passwords_racoon(temp_dir, temp_dir, "Treated_passwords_racoon.txt")
        extract_passwords_redline(temp_dir, temp_dir, "Treated_passwords_redline.txt")

        racoon_data, redline_data = "", ""
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8", errors="ignore") as f:
                racoon_data = f.read()

        if os.path.exists(output_file2):
            with open(output_file2, "r", encoding="utf-8", errors="ignore") as f:
                redline_data = f.read()

        return render_template_string(HTML_PAGE, completed=True, racoon=racoon_data, redline=redline_data)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
