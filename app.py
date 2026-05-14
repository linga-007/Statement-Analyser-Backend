"""
Flask API Server for Bank Statement Analyzer
Provides REST endpoints for file upload and analysis
"""

import os
import sys
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from flask_cors import CORS
from analyzer import analyze_statement

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
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


@app.route("/test", methods=["GET"])
def test_endpoint():
    """Simple test endpoint for frontend/backend connectivity checks"""
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
        # Check if file is in request
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]

        # Check if file is selected
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                "error": f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400

        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Analyze the file
        result = analyze_statement(filepath)

        # Clean up temporary file
        try:
            os.remove(filepath)
        except Exception:
            pass

        return jsonify(to_serializable(result)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/analyze-multiple", methods=["POST"])
def analyze_multiple():
    """
    Analyze multiple uploaded bank statement files
    Accepts: multipart/form-data with multiple 'files' fields
    Returns: JSON array with analysis results for each file
    """
    try:
        # Check if files are in request
        if "files" not in request.files:
            return jsonify({"error": "No files provided"}), 400

        files = request.files.getlist("files")

        if not files or files[0].filename == "":
            return jsonify({"error": "No files selected"}), 400

        results = []
        filepaths = []

        # Process each file
        for file in files:
            try:
                # Check file extension
                if not allowed_file(file.filename):
                    results.append({
                        "name": file.filename,
                        "status": "error",
                        "error": f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
                    })
                    continue

                # Save file temporarily
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                filepaths.append(filepath)

                # Analyze the file
                result = analyze_statement(filepath)
                results.append(result)

            except Exception as e:
                results.append({
                    "name": file.filename,
                    "status": "error",
                    "error": str(e)
                })

        # Clean up temporary files
        for filepath in filepaths:
            try:
                os.remove(filepath)
            except Exception:
                pass

        return jsonify(to_serializable(results)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        "error": f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.0f} MB"
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
