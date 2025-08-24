
Adv. Shah Fahad — Flask Website (Python + HTML/CSS/JS)
======================================================

How to run (Windows / macOS / Linux)
------------------------------------
1) Ensure Python 3.10+ is installed.
2) In terminal, go inside the project folder:
   > python -m venv venv
   > venv\Scripts\activate    (Windows)   OR   source venv/bin/activate (macOS/Linux)
   > pip install -r requirements.txt
   > python app.py
3) Open http://127.0.0.1:5000 in your browser.

Admin Panel
-----------
- URL: http://127.0.0.1:5000/admin/login
- Username: shahfahad
- Password: vaih53747

Content Editing
---------------
- Home hero title/subtitle, bio, stats, portrait upload
- Services: add/update rows
- Cases: add/update rows
- Contact messages saved to data/messages.json

Files of interest
-----------------
- app.py                (Flask server)
- templates/*.html      (pages & admin)
- static/css/styles.css (styles)
- static/images/portrait.jpg
- data/*.json           (content storage)
