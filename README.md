Flask Job Portal

Setup:
1. (Optional) create and activate virtual environment:
   python3 -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate    # Windows PowerShell

2. Install requirements:
   pip install -r requirements.txt

3. Create database and seed sample jobs:
   python create_db.py

4. Run app:
   python app.py

5. Open in browser:
   http://127.0.0.1:5000/

Admin login:
username: admin
password: admin

Uploads saved to static/uploads
