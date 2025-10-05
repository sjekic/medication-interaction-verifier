# medication-interaction-verifier

 MedAid, the medication interaction verifier, is a simple web application that allows users to input two medications and see the potential side effects/contraindications for the interaction between them. The database was built using SQLite and filled in manually using data from a verified online resource. The frontend is built using html and the backend is built using python. The functionalities of the app include CRUD operations like adding missing drug interactions or seeing the existing ones in the database using FastAPI. All of the searches done by the user are saved into a JSON file. It also has a page dedicated to looking up the closest pharmacies in the area.

Setup instructions:

git clone https://github.com/<your-username>/medication-interaction-verifier.git
cd medication-interaction-verifier

python -m venv venv
Windows:
venv\Scripts\activate
macOS/Linux:
source venv/bin/activate

When activating the virtual environment, an error might occur on Windows Powershell that says that running scripts is disabled on this system. In this case run the following command: Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
And then: venv\Scripts\activate

pip install -r requirements.txt

Then you can run the seed.py file, and type the following into the terminal:
uvicorn main:app --reload

and if using VSCode you can click go live (while being in the index.html file) or open the following link in the browser:
http://127.0.0.1:5500/app/static/
