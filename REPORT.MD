# Medication Interaction Verifier
## MedAid by Simonida Jekic

In order to fix code smells, I changed the severity string literals for a VALID_SEVERITIES constant and reused it in rule update and creation. This way I reduced duplication.

In the first assignment the application was tested out by simply doing verification through the browser and HTTP tools, without any automated tests. I used pytest along with pytest-cov to run the tests and measure their coverage. All 12 tests passed successfully, including unit-like tests that test out a single function like:
* normalize_pair (which trims and makes strings lowercase, and ensure that pairs of drugs which the user inputs are order-independent)
* ensure_history_file (if the history file does not exist, it should be created and initialized, but instead of the test using the actual directory and file, it creates temporary ones)
* get_history(limit) (manually writes two entries to the temporary file and checks if only one entry, the last one, is returned)
as well as integration tests:
* test_api_check (tests the /check endpoint through FastAPI's TestClient which is used for testing without running a real HTTP server, it does a POST /check with a known pair of drugs and asserts HTTP status 200 with valid values for severity and description, but also with a pair of fake names of drugs which assert 'found' as false, 'suggest_add' as true, null/None for severity and description)
* test_api_rules (tests CRUD (Create, Remove, Update, Delete) operations on interactions, first by checking if the endpoint returns a non-empty list, then when we specify an existing id it checks if 200 is returned with the correct rule data, or 404 for a non-existing id, furthermore, it tests the entire POST-PUT-DELETE lifecycle and if 400 bad request is returned when a non-existing severity is specified) 
* test_health (checks the overall app status and database status)
* test_metrics (verifies the /metrics endpoint used for monitoring by calling GET /metrics with TestClient and asserting status 200 to ensure that the app is correctly exposing metrics such as request counts, latencies and error information)
The overall test coverage is 91%, 95% for the main file.

To make the application easier to run and deploy I containerized the project using Docker. I used a lightweight Python base image and added the Dockerfile to the root of the project. It sets /app as the working directory and installs tools for Python and dependencies, then copies the application code into the image and seeds the SQLite database. In the end it exposes port 8000 and starts FastAPI with uvicorn.