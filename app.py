import os, io, hmac, tempfile, shutil, base64, mimetypes, re
from functools import wraps
from flask import Flask, request, render_template_string, send_file, Response, send_from_directory

import get_hex
from generate_report import generate_report

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB
app.secret_key = os.getenv("FLASK_SECRET", "dev-change-me")

USER = os.getenv("APP_USER", "")
PASS = os.getenv("APP_PASS", "")

def check_auth(u, p):
    return hmac.compare_digest(u or "", USER) and hmac.compare_digest(p or "", PASS)

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not USER or not PASS:
            return f(*args, **kwargs)  # dev mode if creds not set
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Login"'})
        return f(*args, **kwargs)
    return wrapper

# ---- Load Semke logo as base64 (optional) -----------------------------------
SEMKE_IMG_TAG = ""
try:
    logo_path = os.path.join(os.path.dirname(__file__), "static", "semke.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as imgf:
            b64 = base64.b64encode(imgf.read()).decode("ascii")
        SEMKE_IMG_TAG = f'<img src="data:image/png;base64,{b64}" alt="Logo">'
except Exception:
    SEMKE_IMG_TAG = ""

# ---- Template: centered 800x800 table, Verdana, color box, hidden links -----
HTML = """<!doctype html>
<title>Bendix Decoder</title>
<style>
  body {
    font-family: Verdana, sans-serif;
    background-color: #f5f5f5;
  }
  table.outer {
    border: 2px solid #333;
    width: 800px;
    height: 800px;
    margin: auto;
    margin-top: 50px;
    background-color: white;
    border-collapse: collapse;
  }
  td.cell {
    vertical-align: top;
    padding: 20px;
    text-align: center;
  }
  .color-box {
    width: 500px;
    height: 10px;
    border: 1px solid #333;
    margin: 10px auto 0 auto;
    background-color: lightgray; /* default when neither is checked */
  }
  form { margin-bottom: 1rem; }
</style>

<table class="outer">
  <tr>
    <td class="cell">
      <div style="text-align:center; margin-bottom: 8px;">
        __SEMKE_IMG__
      </div>

      <h1>Upload source file</h1>
      <form method="post" enctype="multipart/form-data">
        <input type="file" name="file" required><br><br>

        <label><input type="checkbox" name="fancy" id="fancy"> Enhance Results</label>
        <label style="margin-left:1rem;"><input type="checkbox" name="charts" id="charts"> Create Charts</label>

        <div id="colorBox" class="color-box" title="Option indicator"></div>

        <br>
        <button type="submit">Process</button>
      </form>

      {% if ready %}
        <hr>
        <p>VIN: <b>{{ vin }}</b></p>
        <p><a href="/download?token={{ token }}">Download self-contained HTML</a></p>
        <p><a href="/view?token={{ token }}" target="_blank">View report</a></p>
      {% endif %}
    </td>
  </tr>
</table>

<script>
function updateColor() {
  const fancy = document.getElementById("fancy").checked;
  const charts = document.getElementById("charts").checked;
  const box = document.getElementById("colorBox");
  if (!fancy && !charts) {
    box.style.backgroundColor = "lightgray";
  } else if (fancy && !charts) {
    box.style.backgroundColor = "blue";
  } else if (!fancy && charts) {
    box.style.backgroundColor = "crimson";
  } else {
    box.style.backgroundColor = "purple";
  }
}
document.getElementById("fancy").addEventListener("change", updateColor);
document.getElementById("charts").addEventListener("change", updateColor);
window.onload = updateColor;
</script>
"""

# Substitute the base64 logo (or blank if not available)
HTML = HTML.replace("__SEMKE_IMG__", SEMKE_IMG_TAG)

RESULTS = {}
# RESULTS[token] = {
#   "vin": str,
#   "bytes": html_bytes_with_web_paths,  # for /view
#   "base_dir": /tmp/.../reports/<vin>,
#   "workdir": /tmp/...,
# }

# ------------------------- Helpers for base64 inlining ------------------------

_ASSET_RE = re.compile(r'''(?P<attr>src|href)=["'](?P<path>(html|charts)/[^"']+)["']''', re.IGNORECASE)

def _guess_mime(path):
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        if path.lower().endswith(".png"): return "image/png"
        if path.lower().endswith(".gif"): return "image/gif"
        if path.lower().endswith(".jpg") or path.lower().endswith(".jpeg"): return "image/jpeg"
    return mime or "application/octet-stream"

def _embed_local_assets(html_text: str, base_dir: str) -> bytes:
    """
    Replace src/href="html/...|charts/..." with data: URIs using files under base_dir.
    """
    cache = {}  # relpath -> datauri
    def _repl(m):
        rel = m.group("path")
        if rel in cache:
            return f'{m.group("attr")}="{cache[rel]}"'
        abs_path = os.path.abspath(os.path.join(base_dir, rel))
        # ensure path stays inside base_dir
        if not abs_path.startswith(os.path.abspath(base_dir) + os.sep):
            return m.group(0)
        if not os.path.exists(abs_path):
            return m.group(0)
        with open(abs_path, "rb") as f:
            b = f.read()
        mime = _guess_mime(abs_path)
        datauri = f"data:{mime};base64,{base64.b64encode(b).decode('ascii')}"
        cache[rel] = datauri
        return f'{m.group("attr")}="{datauri}"'

    inlined = _ASSET_RE.sub(_repl, html_text)
    return inlined.encode("utf-8")

# --------------------------------- Routes ------------------------------------

@app.route("/", methods=["GET", "POST"])
@require_auth
def index():
    if request.method == "GET":
        return render_template_string(HTML, ready=False)

    f = request.files.get("file")
    if not f or f.filename == "":
        return render_template_string(HTML, ready=False)

    fancy = bool(request.form.get("fancy"))
    charts = bool(request.form.get("charts"))

    workdir = tempfile.mkdtemp(prefix="absreport_")
    try:
        src_path = os.path.join(workdir, f.filename)
        f.save(src_path)

        vin, data, fMode, chartsOpt = get_hex.select_from_path(src_path, fancy=fancy, charts=charts)

        # This writes assets/charts under workdir/reports/<vin>/{html,charts}
        raw_report = generate_report(vin=vin, data=data, fMode=fMode, chartsOpt=chartsOpt, output_root=workdir)

        token = os.urandom(16).hex()
        base_dir = os.path.join(workdir, "reports", vin)

        # For in-browser viewing we keep file paths and serve via /asset
        html_view = raw_report.decode("utf-8", errors="ignore")
        for prefix in ["src", "href"]:
            html_view = html_view.replace(f'{prefix}="html/',  f'{prefix}="/asset/{token}/html/')
            html_view = html_view.replace(f"{prefix}='html/",  f"{prefix}='/asset/{token}/html/")
            html_view = html_view.replace(f'{prefix}="charts/',f'{prefix}="/asset/{token}/charts/')
            html_view = html_view.replace(f"{prefix}='charts/",f"{prefix}='/asset/{token}/charts/")

        RESULTS[token] = {
            "vin": vin,
            "bytes": html_view.encode("utf-8"),  # for /view
            "base_dir": base_dir,
            "workdir": workdir,
        }
        workdir = None
        return render_template_string(HTML, ready=True, vin=vin, token=token)
    finally:
        if workdir and os.path.exists(workdir):
            shutil.rmtree(workdir, ignore_errors=True)

@app.route("/view")
@require_auth
def view():
    token = request.args.get("token")
    obj = RESULTS.get(token)
    if not obj:
        return "Not found", 404
    return Response(obj["bytes"], mimetype="text/html")

@app.route("/download")
@require_auth
def download():
    token = request.args.get("token")
    obj = RESULTS.get(token)
    if not obj:
        return "Not found", 404

    # Inline ALL local assets as base64 so the HTML is standalone.
    base_dir = obj["base_dir"]
    html_text = obj["bytes"].decode("utf-8", errors="ignore")
    # Our /view HTML has /asset/<token>/... URLs; switch them back to relative so we can inline.
    html_text = re.sub(r'/asset/[^/]+/(html|charts)/', r'\1/', html_text)
    inlined_bytes = _embed_local_assets(html_text, base_dir)

    return send_file(
        io.BytesIO(inlined_bytes),
        as_attachment=True,
        download_name=f"{obj['vin']}_report.html",
        mimetype="text/html"
    )

@app.route("/asset/<token>/<path:subpath>")
@require_auth
def asset(token, subpath):
    obj = RESULTS.get(token)
    if not obj:
        return "Not found", 404
    base_dir = obj["base_dir"]
    safe_base = os.path.abspath(base_dir)
    target = os.path.abspath(os.path.join(base_dir, subpath))
    if not target.startswith(safe_base + os.sep) and target != safe_base:
        return "Bad path", 400
    if not os.path.exists(target):
        return "Not found", 404
    directory = os.path.dirname(target)
    filename = os.path.basename(target)
    return send_from_directory(directory, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
