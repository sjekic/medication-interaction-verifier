# medication-interaction-verifier

 MedAid, the medication interaction verifier, is a simple web application that allows users to input two medications and see the potential side effects/contraindications for the interaction between them. The database was built using SQLite and filled in manually using data from a verified online resource. The frontend is built using html and the backend is built using python. The functionalities of the app include CRUD operations like adding missing drug interactions or seeing the existing ones in the database using FastAPI. All of the searches done by the user are saved into a JSON file. It also has a page dedicated to looking up the closest pharmacies in the area.

### Setup instructions:

git clone https://github.com/sjekic/medication-interaction-verifier.git
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

The frontend is served at http://127.0.0.1:8000/ with pages for /rules, /history and /pharmacies.

The API docs are on /docs, the health check on /health and metrics on /metrics.

### Running tests
To run the tests with coverage input the following snippet into the terminal:
pytest tests --cov=. --cov-report=term-missing
and to run them with the condition of 70% of tests passing for the CI to work:
pytest tests --cov=. --cov-report=term-missing --cov-fail-under=70
A sample test report is included under the file name tests_report.txt

### Running with Docker
The app can also be ran with Docker by building the image:
docker build -t medaid-app .
and running the container
docker run -p 8000:8000 medaid-app
and accessed through http://localhost:8000

### CI/CD, Azure and Metrics
CI/CD pipeline is implemented with Github Actions in .github/workflow/ci.yml

The app is deployed using Azure Web App for Containers using the Docker image pushed from CI.

For monitoring and health checks I provided GET /health which checks the overall app and database status and GET /metrics that gives Prometheus compatible metrics.