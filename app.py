import os
import uuid
import atexit
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from prisma import Prisma
from ai import analyze_image

app = Flask(__name__, template_folder="templates")
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB file limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif'}

db = Prisma()
try:
    if not db.is_connected():
        db.connect()
except Exception as e:
    print(f"[WARN] Prisma initial connection failed: {e}")

atexit.register(lambda: db.disconnect() if db.is_connected() else None)

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File exceeds the 16MB limit"}), 413

@app.route("/style.css")
def css():
    return send_from_directory(os.path.join(app.root_path, 'templates'), 'style.css')

@app.route("/js/system.js")
def serve_js():
    root_js_dir = os.path.join(app.root_path, 'js')
    template_js_dir = os.path.join(app.root_path, 'templates', 'js')
    
    if os.path.exists(os.path.join(root_js_dir, 'system.js')):
        return send_from_directory(root_js_dir, 'system.js')
    elif os.path.exists(os.path.join(template_js_dir, 'system.js')):
        return send_from_directory(template_js_dir, 'system.js')
    else:
        return jsonify({"error": "system.js not found on disk"}), 404

@app.route("/")
def index():    
    return render_template('index.html')

@app.route("/analyze", methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file attached"}), 400
        
    file = request.files['file']
    
    if not file or file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({
            "error": f"Invalid file type '{ext}'. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        }), 400
        
    raw_basename = os.path.splitext(file.filename)[0]
    safe_basename = secure_filename(raw_basename) or "upload"
    unique_filename = f"{uuid.uuid4().hex}_{safe_basename}{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

    file.save(filepath)
    user_query = request.form.get('query', '').strip()

    try:
        audit_json = analyze_image(filepath, user_query)

        if not isinstance(audit_json, dict):
            if isinstance(audit_json, list) and len(audit_json) > 0 and isinstance(audit_json[0], dict):
                audit_json = audit_json[0]
            else:
                audit_json = {
                    "vulnerability": "Security Analysis Note",
                    "severity": "Info",
                    "remediation": str(audit_json)
                }

        vuln = str(audit_json.get("vulnerability") or "Unspecified Flaw")
        sev = str(audit_json.get("severity") or "Medium")
        rem = str(audit_json.get("remediation") or "N/A")

        if not db.is_connected():
            db.connect()

        db.securitylog.create(
            data={
                "vulnerability": vuln,
                "severity": sev,
                "remediation": rem
            }
        )

        return jsonify(audit_json), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass

if __name__ == '__main__':
    app.run(debug=True, port=8080)