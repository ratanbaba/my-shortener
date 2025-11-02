import os
from flask import Flask, request, redirect, jsonify
import hashlib, time, sqlite3, validators

app = Flask(__name__)
DB = "urls.db"

def init_db():
    with sqlite3.connect(DB) as c:
        c.execute("CREATE TABLE IF NOT EXISTS urls (code TEXT PRIMARY KEY, url TEXT, clicks INTEGER DEFAULT 0)")

init_db()

def short_code(url):
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    while True:
        h = hashlib.md5(f"{url}{time.time()}".encode()).hexdigest()
        code = "".join(chars[int(h[i:i+2], 16) % 62] for i in range(0, 12, 2))
        with sqlite3.connect(DB) as c:
            if not c.execute("SELECT 1 FROM urls WHERE code=?", (code,)).fetchone():
                return code

@app.route("/shorten", methods=["POST", "GET"])
def shorten():
    if request.method == "GET":
        url = request.args.get("long_url", "").strip()
    else:
        data = request.get_json() or {}
        url = data.get("long_url", "").strip()
    
    if not url:
        return "<h3>URL daal bhai!</h3><p>Example: ?long_url=https://google.com</p>"
    
    if not validators.url(url):
        url = "http://" + url
    if not validators.url(url):
        return "<h3>Galat URL!</h3>"

    code = short_code(url)
    with sqlite3.connect(DB) as c:
        c.execute("INSERT INTO urls (code, url) VALUES (?, ?)", (code, url))
    
    short = f"{request.host_url}{code}"
    return f"""
    <h2>Short Link Ban Gaya!</h2>
    <p><a href="{short}" target="_blank">{short}</a></p>
    <hr>
    <form>
      <input type="text" name="long_url" placeholder="Naya URL daal" size="50">
      <button type="submit">Short Kar!</button>
    </form>
    """

@app.route("/<code>")
def go(code):
    with sqlite3.connect(DB) as c:
        row = c.execute("SELECT url FROM urls WHERE code=?", (code,)).fetchone()
        if row:
            c.execute("UPDATE urls SET clicks = clicks + 1 WHERE code=?", (code,))
            return redirect(row[0])
    return "<h3>Nahi mila!</h3>"

@app.route("/")
def home():
    return """
    <h1>Mera URL Shortener</h1>
    <form>
      <input type="text" name="long_url" placeholder="https://youtube.com/..." size="60">
      <button type="submit">Short Kar!</button>
    </form>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
