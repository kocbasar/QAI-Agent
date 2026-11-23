# QAI-Agent

## Web UI smoke tests

UI smoke tests use Playwright and run only against the test environment.
They never use production credentials or a production URL.

1. Copy `.env.example` to a local `.env` file and set the real values:

   ```env
   UI_TEST_BASE_URL=https://test.example.com
   UI_TEST_USERNAME=your-test-user
   UI_TEST_PASSWORD=your-test-password
   ```

2. Install Python dependencies and the Chromium browser:

   ```bash
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

3. Run the smoke test:

   ```bash
   pytest -q tests/test_ui_smoke.py
   ```

The smoke test is skipped when `UI_TEST_BASE_URL` is not configured.
