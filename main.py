import os
from flask import Flask
from log_parser_body import (
    extract_passwords_racoon,
    extract_passwords_redline
)
from cc_parser import process_cc, process_cc_v2

app = Flask(__name__)

def run_parser():
    try:
        main_folder = input("Specify the main folder: ")
    except EOFError:
        main_folder = os.getenv("MAIN_FOLDER", ".")
    
    print(f"The main folder is: {main_folder}")
    
    output_folder = main_folder
    process_cc(main_folder)
    process_cc_v2(main_folder)
    output_file = "Treated_passwords_racoon.txt"
    output_file2 = "Treated_passwords_redline.txt"
    extract_passwords_racoon(main_folder, output_folder, output_file)
    extract_passwords_redline(main_folder, output_folder, output_file2)

@app.route("/")
def home():
    run_parser()
    return "Parser ran successfully!"

if __name__ == "__main__":
    # Binds to the port Railway exposes
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
