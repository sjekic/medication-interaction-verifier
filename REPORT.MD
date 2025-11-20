# Medication Interaction Verifier
## MedAid by Simonida Jekic

### Functionality
MedAid or Medication Interaction Verifier allows users to input 2 drug names, regardless of order and lowercase/uppercase formatting, and check if there exists an interaction between them that could potentially have negative consequences on the user's health. Furthermore, the app allows users to add interactions to the database if the one they looked up could not be found, but also delete or update existing ones. It also has an interactive map that shows users the nearest pharmacies to their current location. 

The architecture consists of a backend that is implemented in main.py and uses FastAPI. It exposes:
* POST /check
* GET /rules
* POST /rules
* GET /history
* GET /health
* GET /metrics

FastAPI also serves the static frontend, which is a very lightweight HTML/Javascript UI.

In terms of the database, it is using SQLite for storing interaction rules and the seed.py file is responsible for creating the schema and seeding the rules. Regarding storing the interaction history, each new interaction search is appended to the history file and by calling the get_history(limit) we can get the last N entries.

In the first version, the deployment was on local host, there were no automated tests, nor CI/CD pipeline. Now it is reliable, testable and deployable. First I fixed the code where it was necessary, created 12 tests that cover more than 90% of the app

### Code Quality and Testing
In order to fix code smells, I changed the severity string literals for a VALID_SEVERITIES constant and reused it in rule update and creation. This way I reduced duplication.

Frontend no longer hardcodes http://local.host:8000 but instead window.location.origin, which follows the configuration over hard coding idea.

In the first version the application was tested out by simply doing verification through the browser and HTTP tools, without any automated tests. I used pytest along with pytest-cov to run the tests and measure their coverage. All 12 tests passed successfully, including unit-like tests that test out a single function like:
* normalize_pair (which trims and makes strings lowercase, and ensure that pairs of drugs which the user inputs are order-independent)
* ensure_history_file (if the history file does not exist, it should be created and initialized, but instead of the test using the actual directory and file, it creates temporary ones)
* get_history(limit) (manually writes two entries to the temporary file and checks if only one entry, the last one, is returned)

as well as integration tests:
* test_api_check (tests the /check endpoint through FastAPI's TestClient which is used for testing without running a real HTTP server, it does a POST /check with a known pair of drugs and asserts HTTP status 200 with valid values for severity and description, but also with a pair of fake names of drugs which assert 'found' as false, 'suggest_add' as true, null/None for severity and description)
* test_api_rules (tests CRUD (Create, Remove, Update, Delete) operations on interactions, first by checking if the endpoint returns a non-empty list, then when we specify an existing id it checks if 200 is returned with the correct rule data, or 404 for a non-existing id, furthermore, it tests the entire POST-PUT-DELETE lifecycle and if 400 bad request is returned when a non-existing severity is specified) 
* test_health (checks the overall app status and database status)
* test_metrics (verifies the /metrics endpoint used for monitoring by calling GET /metrics with TestClient and asserting status 200 to ensure that the app is correctly exposing metrics such as request counts, latencies and error information)

The overall test coverage is 91%, 95% for the main file. The --cov-fail-under=70 flag in pytest ensures that if coverage drops below 70% in the future, the pipeline will fail.

### Continuous Integration
I created a ci.yml file under .github/workflows/ which implements automated testing and building on every push and pull request. The test job runs on ubuntu-latest, checks out the repository, sets up python, installs dependencies from the requirements.txt, seeds the base and runs tests with coverage.

### Continuous Deployment
To make the application easier to run and deploy I containerized the project using Docker. I used a lightweight Python base image and added the Dockerfile to the root of the project. It sets /app as the working directory and installs tools for Python and dependencies, then copies the application code into the image and seeds the SQLite database. In the end it exposes port 8000 and starts FastAPI with uvicorn. The ci.yml file also contains the docker-build-and-push which acts as a deployment step. It runs only the main branch by specifying refs/head/main. It logs into Docker hub using DOCKERHUB_USERNAME and DOCKERHUB_TOKEN which I added to github secrets. It also builds and pushes the image :latest and :commit-sha

In terms of Azure web app deployment, I created the web app in the resource group with the location of Central Spain in order to minimize latency. For the configuration I chose the option for deploying containers, using https://index.docker.io as the source, simonidajekic/medaid-app as the image, latest as the tag and the WEBSITE_PORT = 8000. So the web app pulls the image simonidajekic/medaid-app:latest from Docker hub and runs the container. 

In case the CI is pipeline pushes a new image, it will pull the latest image, it just requires restarting the Azure web app in order to pull it and run it.

Users access the application through https://medication-interaction-verifier-dxhzchfhfqd5c7g0.spaincentral-01.azurewebsites.net/ which presents the frontend UI, /docs that exposes the API docs, /health the health check and /metrics the metrics - more about it in the next section.

### Health Checks and Monitoring
To support observability and runtime diagnostics, the app exposes both a /health endpoint and prometheus compatible metrics. The get /health endpoint returns a JSON with the overall app's status and the state of the database connection. This allows for fast checks without going through the entire business logic. Some of the things that can be checked in this way are the uptime monitor, load balancer and the CI smoke test. If more detailed and specific metrics are necessary, they can be accessed by using the get /metrics request, which is integrated by using prometheus-fastapi-instrumentator. The prometheus.yml scrapes the service at port 8000 every 10 seconds. This returns metrics like requests per method, histograms of request latency and python runtime metrics. The screenshot below shows a sample of the /metrics output, including HTTP request and python runtime metrics in prometheus format:

![Prometheus metrics endpoint](docs/images/prometheus-metrics.png)

### DevOps Benefits
Although this is a small project, devops practice are extremely beneficial. Not only is the app now easily accessible from any device, including mobile phones, but also ensures it runs on any device when ran locally, due to the Docker containerization. I can also continuously monitor if everything is well and the metrics. These practices are important for any project, but especially in the healthtech industry where everything needs to be very reliable.


