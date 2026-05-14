"""
Vercel serverless function handler for Bank Statement Analyzer
"""

import os
import sys

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from flask_cors import CORS
from analyzer import analyze_statement

# Initialize Flask app
app = Flask(__name__)

# Configure CORS - accept requests from any Vercel frontend and localhost
CORS(app, 
     origins=r".*vercel\.app$|http://localhost.*|http://127\.0\.0\.1.*",
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True,
     max_age=3600)

# Configuration
UPLOAD_FOLDER = "/tmp/uploads"
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "xlsm", "pdf"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


def to_serializable(value):
    """Recursively convert pandas/numpy scalar values into native Python types."""
    if isinstance(value, dict):
        return {k: to_serializable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_serializable(v) for v in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return value
    return value


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Bank Statement Analyzer API",
        "version": "1.0.0"
    }), 200


@app.route("/api", methods=["GET"])
def api_health():
    """Health check endpoint for /api route"""
    return jsonify({
        "status": "ok",
        "message": "Bank Statement Analyzer API",
        "version": "1.0.0"
    }), 200


@app.route("/test", methods=["GET"])
def test_endpoint():
    """Simple test endpoint for frontend/backend connectivity checks"""
    return jsonify({
        "status": "ok",
        "message": "Test endpoint reached successfully",
        "service": "bank-statement-analyzer-backend"
    }), 200


@app.route("/api/test", methods=["GET"])
def api_test_endpoint():
    """Simple test endpoint for /api route"""
    return jsonify({
        "status": "ok",
        "message": "Test endpoint reached successfully",
        "service": "bank-statement-analyzer-backend"
    }), 200


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze uploaded bank statement file
    Accepts: multipart/form-data with 'file' field
    Returns: JSON with analysis results
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({
                "error": f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        result = analyze_statement(filepath)

        try:
            os.remove(filepath)
        except Exception:
            pass

        return jsonify(to_serializable(result)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """Analyze endpoint for /api route"""
    return analyze()


@app.route("/analyze-multiple", methods=["POST"])
def analyze_multiple():
    """
    Analyze multiple uploaded bank statement files
    Accepts: multipart/form-data with multiple 'files' fields
    Returns: JSON array with analysis results for each file
    """
    try:
        if "files" not in request.files:
            return jsonify({"error": "No files provided"}), 400

        files = request.files.getlist("files")

        if not files or files[0].filename == "":
            return jsonify({"error": "No files selected"}), 400

        results = []
        filepaths = []

        for file in files:
            try:
                if not allowed_file(file.filename):
                    results.append({
                        "name": file.filename,
                        "status": "error",
                        "error": f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
                    })
                    continue

                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                filepaths.append(filepath)

                result = analyze_statement(filepath)
                results.append(result)

            except Exception as e:
                results.append({
                    "name": file.filename,
                    "status": "error",
                    "error": str(e)
                })

        for filepath in filepaths:
            try:
                os.remove(filepath)
            except Exception:
                pass

        return jsonify(to_serializable(results)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze-multiple", methods=["POST"])
def api_analyze_multiple():
    """Analyze multiple endpoint for /api route"""
    return analyze_multiple()


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "error": f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.0f} MB"
    }), 413


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500
