from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os, json

app = Flask(__name__)
app.secret_key = "change-this-secret"  # change later

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMG_PATH = os.path.join(BASE_DIR, "static", "images", "portrait.jpg")

def dp(path): return os.path.join(DATA_DIR, path)

# ---- Defaults (first run) ----
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json(name, default):
    p = dp(name)
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default
    with open(p, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return default

def save_json(name, data):
    with open(dp(name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

SITE = load_json("site.json", {
    "title": "Adv. Shah Fahad — Lawyer",
    "tagline": "Advocate — Peshawar (KPK)",
    "hero_title": "Advocate Shah Fahad",
    "hero_sub": "Lawyer — Peshawar (KPK) | 2 yrs Peshawar, 1 yr Puran Aloch",
    "bio": "I am an advocate by profession based in Peshawar, Khyber Pakhtunkhwa. Graduated BS LLB from University of Swat. Practising in Peshawar and previously in Puran Aloch. Focused on client-first representation, clear communication, and timely case progress.",
    "stats": {"won": 19, "lost": 2, "total": 21},
    "phone": "03055003519",
    "email": "advfahadsafi@gmail.com",
    "address": "Momand, KPK — Practising in Peshawar & Puran Aloch"
})
SERVICES = load_json("services.json", [
  {"title": "Civil Litigation", "desc": "Property disputes, contracts, recovery suits, and injunction matters."},
  {"title": "Criminal Defense", "desc": "Bail, trial strategy, and appeals with a focus on rights & due process."},
  {"title": "Family Law", "desc": "Nikah, divorce/khula, maintenance, guardianship, custody."},
  {"title": "Corporate & Tax", "desc": "Business contracts, company matters, and tax compliance guidance."}
])
CASES = load_json("cases.json", [
  {"title": "Civil Suit — Property Injunction", "court": "Peshawar", "year": "2023", "result": "Decree in favour of plaintiff (won)."},
  {"title": "Criminal Appeal — Bail", "court": "Peshawar", "year": "2024", "result": "Bail granted by appellate court (won)."}
])
MESSAGES = load_json("messages.json", [])

# ----- Simple auth (username/password in config JSON) -----
AUTH = load_json("auth.json", {
    "username": "shahfahad",
    "password_hash": generate_password_hash("vaih53747")  # change from admin
})

def is_logged_in():
    return session.get("logged_in") is True

@app.context_processor
def inject_globals():
    return dict(SITE=SITE)

# ---- Public Routes ----
@app.route("/")
def home():
    return render_template("index.html", site=SITE, services=SERVICES, cases=CASES[:3])

@app.route("/about")
def about():
    return render_template("about.html", site=SITE)

@app.route("/services")
def services():
    return render_template("services.html", services=SERVICES)

@app.route("/cases")
def cases_view():
    return render_template("cases.html", cases=CASES)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        message = request.form.get("message", "")
        MESSAGES.append({"name": name, "email": email, "message": message, "ts": __import__("datetime").datetime.utcnow().isoformat()+"Z"})
        save_json("messages.json", MESSAGES)
        flash("Thanks! Your message has been received.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

# ---- Admin Routes ----
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    error = ""
    if request.method == "POST":
        u = request.form.get("username","")
        p = request.form.get("password","")
        if u == AUTH["username"] and check_password_hash(AUTH["password_hash"], p):
            session["logged_in"] = True
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid credentials"
    return render_template("admin_login.html", error=error)

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("admin_login"))

@app.route("/admin", methods=["GET"])
def admin_dashboard():
    if not is_logged_in():
        return redirect(url_for("admin_login"))
    return render_template("admin_dashboard.html", site=SITE, services=SERVICES, cases=CASES)

@app.route("/admin/save_site", methods=["POST"])
def admin_save_site():
    if not is_logged_in():
        return redirect(url_for("admin_login"))
    SITE["hero_title"] = request.form.get("hero_title", SITE["hero_title"])
    SITE["hero_sub"] = request.form.get("hero_sub", SITE["hero_sub"])
    SITE["bio"] = request.form.get("bio", SITE["bio"])
    SITE["stats"]["won"] = int(request.form.get("won", SITE["stats"]["won"]))
    SITE["stats"]["lost"] = int(request.form.get("lost", SITE["stats"]["lost"]))
    SITE["stats"]["total"] = int(request.form.get("total", SITE["stats"]["total"]))
    # replace portrait
    file = request.files.get("portrait")
    if file and file.filename:
        file.save(IMG_PATH)
    save_json("site.json", SITE)
    flash("Site content saved.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/save_services", methods=["POST"])
def admin_save_services():
    if not is_logged_in():
        return redirect(url_for("admin_login"))
    titles = request.form.getlist("title[]")
    descs = request.form.getlist("desc[]")
    new = []
    for i, t in enumerate(titles):
        t = t.strip()
        if not t: continue
        new.append({"title": t, "desc": descs[i] if i < len(descs) else ""})
    SERVICES[:] = new
    save_json("services.json", SERVICES)
    flash("Services updated.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/save_cases", methods=["POST"])
def admin_save_cases():
    if not is_logged_in():
        return redirect(url_for("admin_login"))
    titles = request.form.getlist("title[]")
    courts = request.form.getlist("court[]")
    years = request.form.getlist("year[]")
    results = request.form.getlist("result[]")
    new = []
    for i, t in enumerate(titles):
        t = t.strip()
        if not t: continue
        new.append({
            "title": t,
            "court": courts[i] if i < len(courts) else "",
            "year": years[i] if i < len(years) else "",
            "result": results[i] if i < len(results) else ""
        })
    CASES[:] = new
    save_json("cases.json", CASES)
    flash("Cases updated.", "success")
    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
