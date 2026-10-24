from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename  # 1. Critical import added
from prisma import Prisma
import os 
from ai import analyze_image

app = Flask(__name__, template_folder="templates")
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = Prisma()
db.connect()

@app.route("/style.css")
def css():
    return send_from_directory('templates', 'style.css')

@app.route("/js/system.js")
def serve_js():
    root_js_dir = os.path.join(app.root_path, 'js')
    template_js_dir = os.path.join(app.root_path, 'templates', 'js')
    
    # 1. Check if it is in D:\hacktober\js\
    if os.path.exists(os.path.join(root_js_dir, 'system.js')):
        return send_from_directory(root_js_dir, 'system.js')
        
    # 2. Check if it was accidentally placed in D:\hacktober\templates\js\
    elif os.path.exists(os.path.join(template_js_dir, 'system.js')):
        return send_from_directory(template_js_dir, 'system.js')
        
    # 3. Print a strict error to the terminal if it is completely missing
    else:
        print(f"\n[ERROR] system.js NOT FOUND!")
        print(f"Checked Location 1: {root_js_dir}")
        print(f"Checked Location 2: {template_js_dir}\n")
        return jsonify({"error": "File not found on disk"}), 404
@app.route("/")
def index():    
    return render_template('index.html')

@app.route("/analyze", methods=['POST'])
def analyze():
    if 'file' not in request.files:
        # 3. Fixed dictionary syntax (was using sets previously)
        return jsonify({"error": "No file attached"}), 400
        
    # 4. Fixed syntax: request.files uses brackets [], not parentheses ()
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
        
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(filepath)

    try:
        audit_json = analyze_image(filepath)

        # Log to SQLite via Prisma
        db.securitylog.create(
            data={
                "vulnerability": audit_json.get("vulnerability", "Unknown"),
                "severity": audit_json.get("severity", "Unknown"),
                "remediation": audit_json.get("remediation", "None")
            }
        )

        # Clean up the local storage
        os.remove(filepath)
        return jsonify(audit_json), 200

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ensure Prisma disconnects safely when the server stops
    import atexit
    atexit.register(lambda: db.disconnect())
    app.run(debug=True, port=8080)