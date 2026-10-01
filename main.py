import os
from flask import Flask, render_template_string
from log_parser_body import extract_passwords_racoon, extract_passwords_redline
from cc_parser import process_cc, process_cc_v2

app = Flask(__name__)

def run_parser():
    try:
        main_folder = input("Specify the main folder: ")
    except EOFError:
        main_folder = os.getenv("MAIN_FOLDER", ".")
    
    output_folder = main_folder
    output_file = "Treated_passwords_racoon.txt"
    output_file2 = "Treated_passwords_redline.txt"

    # Execute imported functions
    process_cc(main_folder)
    process_cc_v2(main_folder)
    extract_passwords_racoon(main_folder, output_folder, output_file)
    extract_passwords_redline(main_folder, output_folder, output_file2)

@app.route("/")
def home():
    run_parser()

    # Read the results to show them on screen
    racoon_data, redline_data = "", ""
    
    if os.path.exists("Treated_passwords_racoon.txt"):
        with open("Treated_passwords_racoon.txt", "r", encoding="utf-8", errors="ignore") as f:
            racoon_data = f.read()

    if os.path.exists("Treated_passwords_redline.txt"):
        with open("Treated_passwords_redline.txt", "r", encoding="utf-8", errors="ignore") as f:
            redline_data = f.read()

    return render_template_string("""
        <h2>Parser Status: Completed</h2>
        <h3>Racoon Output</h3>
        <pre style="background:#f4f4f4; padding:10px;">{{ racoon if racoon else 'No entries found.' }}</pre>
        <h3>Redline Output</h3>
        <pre style="background:#f4f4f4; padding:10px;">{{ redline if redline else 'No entries found.' }}</pre>
    """, racoon=racoon_data, redline=redline_data)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
