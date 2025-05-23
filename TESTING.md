# Test Configuration and Documentation

## Testing Strategy for Voice-Controlled Application

Testing a voice-controlled application like Julie Julie presents unique challenges, but we can effectively test it by focusing on the **business logic** rather than the voice interface itself.

## Key Testing Principles

### 1. **Separation of Concerns**
- Test the **command processing logic** separately from voice input/output
- Test **individual handlers** in isolation
- Test **API endpoints** independently
- Test **integration** between components

### 2. **Mocking Strategy**
- **Mock speech output** (`subprocess.run` for `say` commands) to prevent actual audio
- **Mock web browser** opening to prevent unwanted browser windows
- **Mock external APIs** (weather, music services) for consistent testing
- **Mock Ollama** integration to avoid dependency on external AI service

### 3. **Test Categories**

#### Unit Tests (`test_command_handlers.py`)
- Test individual command handlers (calculations, music, YouTube, etc.)
- Verify correct response structure
- Test edge cases and error handling
- Ensure non-matching commands return `None`

#### Core Logic Tests (`test_core_logic.py`)
- Test main command processing flow
- Test time and weather functionality
- Test command routing and fallback logic
- Verify proper error handling

#### API Tests (`test_flask_api.py`)
- Test Flask endpoints (`/`, `/command`)
- Test JSON and form data handling
- Test error responses
- Verify API response structure

#### Integration Tests (`test_integration.py`)
- Test complete flow from HTTP request to response
- Test real server startup and communication
- Test various command variations
- End-to-end functionality verification

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-cov requests
```

### Run All Tests
```bash
# Make the test script executable and run
chmod +x run_tests.sh
./run_tests.sh

# Or run directly with pytest
python -m pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Test individual handlers
python -m pytest tests/test_command_handlers.py -v

# Test core application logic
python -m pytest tests/test_core_logic.py -v

# Test API endpoints
python -m pytest tests/test_flask_api.py -v

# Test integration
python -m pytest tests/test_integration.py -v
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

## Test Design Patterns

### 1. **Handler Testing Pattern**
```python
def test_handler_function(self):
    """Test that handler processes commands correctly."""
    result = handle_function("test command")
    
    # Test structure
    self.assertIsNotNone(result)
    self.assertIn("spoken_response", result)
    self.assertIn("opened_url", result)
    self.assertIn("additional_context", result)
    
    # Test content
    self.assertIn("expected_text", result["spoken_response"])
```

### 2. **Mocking Pattern**
```python
@patch('subprocess.run')  # Mock speech output
@patch('webbrowser.open')  # Mock browser opening
def test_with_mocks(self, mock_browser, mock_subprocess):
    """Test with external dependencies mocked."""
    mock_subprocess.return_value = MagicMock(returncode=0)
    
    result = handle_function("test command")
    
    # Verify mocks were called
    mock_subprocess.assert_called()
    mock_browser.assert_called_once()
```

### 3. **API Testing Pattern**
```python
def test_api_endpoint(self):
    """Test API endpoint functionality."""
    response = self.app.post('/command', 
                           json={"text_command": "test"})
    
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data)
    self.assertEqual(data["status"], "success")
```

## Voice Interface Testing Strategy

Since direct voice testing is complex, we focus on:

### 1. **Text Command Testing**
- Test all commands as text input
- Verify command recognition patterns
- Test command variations and synonyms

### 2. **Response Content Testing**
- Verify spoken responses are appropriate
- Test response formatting for speech synthesis
- Ensure responses are clear and helpful

### 3. **Manual Voice Testing**
Use the actual application for voice testing:
```bash
# Run the app
python main.py

# Test voice commands manually:
# 1. Say "Julie Julie"
# 2. Type test commands in the dialog
# 3. Verify spoken responses
```

## Continuous Integration

### GitHub Actions Setup (`.github/workflows/test.yml`)
```yaml
name: Test Julie Julie

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: |
        python -m pytest tests/ --cov=. --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Test Data and Fixtures

### Command Test Cases
```python
TIME_COMMANDS = [
    "what time is it",
    "tell me the time", 
    "current time",
    "what's the clock"
]

CALC_COMMANDS = [
    ("2 + 2", "4"),
    ("5 * 3", "15"),
    ("10 - 4", "6")
]

MUSIC_COMMANDS = [
    "play music on spotify",
    "next song",
    "pause music"
]
```

## Debugging Test Failures

### Common Issues and Solutions

#### 1. **Import Errors**
```bash
# Ensure Python path includes project root
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

#### 2. **Mock Not Working**
```python
# Ensure patch path is correct
@patch('julie_julie_app.subprocess.run')  # Correct module path
```

#### 3. **Server Not Starting in Integration Tests**
```python
# Add sufficient wait time
time.sleep(2)  # Give server time to start
```

#### 4. **External Dependencies**
- Mock all external API calls
- Mock file system operations
- Mock subprocess calls

## Performance Testing

### Response Time Testing
```python
def test_response_time(self):
    """Test that commands respond within acceptable time."""
    start_time = time.time()
    result = process_command_from_user("what time is it")
    end_time = time.time()
    
    self.assertLess(end_time - start_time, 1.0)  # Under 1 second
```

### Memory Usage Testing
```python
import psutil
import os

def test_memory_usage(self):
    """Test that the application doesn't consume excessive memory."""
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    self.assertLess(memory_mb, 100)  # Under 100MB
```

## Test Environment Setup

### Local Development
```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock

# Run tests
python -m pytest tests/ -v
```

### Docker Testing (Optional)
```dockerfile
FROM python:3.10-slim

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install pytest pytest-cov

COPY . /app
WORKDIR /app

CMD ["python", "-m", "pytest", "tests/", "-v"]
```

## Conclusion

This testing framework allows comprehensive testing of Julie Julie without requiring actual voice input/output. The key is to:

1. **Test business logic** separately from voice interface
2. **Mock external dependencies** for consistent results
3. **Test different input variations** to ensure robustness
4. **Use integration tests** to verify complete workflows
5. **Focus on response quality** and correctness

The tests provide confidence that the core functionality works correctly, while manual testing can verify the voice interface experience.
