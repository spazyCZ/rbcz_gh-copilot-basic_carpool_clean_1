# Copilot Instructions

This document provides comprehensive guidelines for generating code using GitHub Copilot in our project. The instructions combine best practices with our specific requirements and default tech stack.

## Objectives
- Generate clear, maintainable, and testing-friendly code.
- Ensure the code includes thorough documentation and data type declarations.
- Encourage the use of primary logging for printing events.
- Produce comprehensive tests with new classes.

## Guidelines

### 1. Documentation and Comments
- Every class and method must have comments explaining their purpose and functionality.
  - Example:
    ```python
    # A class representing a data processor.
    class DataProcessor:
        # Initializes the DataProcessor with initial configuration.
        def __init__(self, config: dict) -> None:
            """
            Initialize with configuration settings.
            
            :param config: Dictionary containing configuration parameters.
            """
            self.config = config
    ```

### 2. Data Type Declarations
- Methods and functions must declare the data types for both parameters and return values.
  - Example:
    ```python
    def add_numbers(a: int, b: int) -> int:
        """
        Adds two integers and returns the sum.
        
        :param a: First integer.
        :param b: Second integer.
        :return: The sum of a and b.
        """
        return a + b
    ```
- Metrics class inheritance of Metric class:
  - All new metrics should inherit from the base Metric class.
  - Ensure that the new metrics class implements all required methods and properties.
    - Example:
      ```python
      class CustomMetric(Metric):
          def calculate(self) -> float:
              # Custom calculation logic
              pass
      ```

### 3. Flask application architecture

- Follow the MVC (Model-View-Controller) pattern:
  - Models: Data structure and business logic using SQLAlchemy
  - Templates: Presentation logic using Jinja2
  - Controllers/Views: Route handlers in Flask blueprints
- Structure your Flask application using blueprints for modularity
- Use application factories for flexible instantiation
- Views should not contain any business logic
- Create service layers for complex business logic
- Data for charts or tables should be fetched via AJAX calls and API endpoints
- All data should be fetched from the database and never hardcoded
- Use Flask-WTF for form validation and cleaning
- Javascript files separate from HTML templates
- Structure your application like this:
  ```
  myapp/
  ├── __init__.py         # Application factory
  ├── models/             # SQLAlchemy models
  ├── views/              # Route handlers organized in blueprints
  ├── templates/          # Jinja2 templates
  ├── static/             # Static files (CSS, JS, images)
  ├── services/           # Business logic
  └── extensions.py       # Flask extensions instantiation
  ```

### 4. Testing Friendly Code
- Code should be written in a manner that facilitates unit testing.
- Separate business logic from UI and external dependencies.
- Use dependency injection where possible to make testing easier.
- EVERY API ENDPOINT MUST HAVE TEST CASES
- Use factories for test data generation
- Use fixtures for common test data setups

### 5. Test Creation with New Classes
- Create separate test classes for new code. These tests should cover different scenarios and edge cases.
- Place tests in designated test files or directories.
- Use a consistent naming convention for test files (e.g., `test_<module_name>_<test_type>.py`).
- SPLIT TESTS INTO MOCK AND INTEGRATION TESTS. NEVER COMBINE THEM INTO ONE FILE
- Set up data before running tests to ensure a clean state.
- Example (using pytest with Flask):
  ```python
  import pytest
  from myapp import create_app
  from myapp.models import MyModel, db
  
  @pytest.fixture
  def app():
      app = create_app('testing')
      with app.app_context():
          db.create_all()
          yield app
          db.drop_all()
  
  @pytest.fixture
  def client(app):
      return app.test_client()
  
  def test_model_creation(app):
      # Test model creation and retrieval
      with app.app_context():
          test_item = MyModel(name="Test Item", value=10)
          db.session.add(test_item)
          db.session.commit()
          assert MyModel.query.count() == 1
          assert MyModel.query.first().name == "Test Item"
  
  def test_view_response(client, app):
      # Test view response with the model
      with app.app_context():
          test_item = MyModel(name="Test Item", value=10)
          db.session.add(test_item)
          db.session.commit()
          item_id = test_item.id
      
      response = client.get(f'/items/{item_id}')
      assert response.status_code == 200
      assert b"Test Item" in response.data
  ```

### 6. Primary Logging for Printing Events
- Use Flask's logging system (which uses Python's standard logging module) instead of print statements.
- Configure logging properly:
  ```python
  import logging
  from flask import Flask
  
  def configure_logging(app):
      handler = logging.FileHandler('flask.log')
      handler.setFormatter(logging.Formatter(
          '%(asctime)s %(levelname)s: %(message)s '
          '[in %(pathname)s:%(lineno)d]'
      ))
      handler.setLevel(logging.INFO)
      app.logger.addHandler(handler)
      app.logger.setLevel(logging.INFO)
  
  app = Flask(__name__)
  configure_logging(app)
  ```
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Example of proper logging in routes:
  ```python
  from flask import Flask, render_template, request, abort
  import logging
  
  app = Flask(__name__)
  logger = app.logger
  
  @app.route('/process')
  def process_data():
      logger.info(f"Processing request from user {request.remote_addr}")
      try:
          # Process request
          result = process_function()
          logger.debug(f"Processed data: {result}")
          return render_template('result.html', result=result)
      except Exception as e:
          logger.error(f"Error processing request: {e}", exc_info=True)
          abort(500)
  ```

### 7. Data Visualization
- Use Chart.js for data visualization.
- Keep JavaScript code separate from HTML.
- Use Jinja2 templates to pass data to the frontend:
  ```python
  # routes.py
  import json
  from flask import render_template
  
  @app.route('/chart')
  def chart_view():
      data = get_chart_data()  # Get data from service or model
      return render_template('chart_template.html', chart_data=json.dumps(data))
  ```
- Implement API endpoints for dynamic data loading:
  ```python
  # routes.py
  from flask import jsonify
  
  @app.route('/api/chart-data')
  def chart_data_api():
      data = get_chart_data()
      return jsonify(data)
  ```
- Structure JavaScript properly:
  ```javascript
  // chart_script.js
  document.addEventListener('DOMContentLoaded', function() {
      const ctx = document.getElementById('myChart').getContext('2d');
      
      // Fetch data from API
      fetch('/api/chart-data')
          .then(response => response.json())
          .then(data => {
              new Chart(ctx, {
                  type: 'bar',
                  data: data,
                  options: {
                      responsive: true,
                      // Other configuration options
                  }
              });
          })
          .catch(error => console.error('Error loading chart data:', error));
  });
  ```

### 8. Security Best Practices
- Always validate and sanitize input parameters from URLs, forms, and APIs.
- Use Flask's security extensions and best practices:
  - Use Flask-WTF for CSRF protection: `{{ form.csrf_token }}`
  - Use SQLAlchemy parameterized queries instead of raw SQL
  - Implement proper permission checks using Flask-Login or Flask-Security
  - Set secure headers using Flask-Talisman
- Protect against common attacks:
  - XSS: Jinja2 templates auto-escape by default; keep this enabled
  - CSRF: Use Flask-WTF's CSRF protection
  - SQL Injection: Use SQLAlchemy and parameterized queries
  - Clickjacking: Set proper X-Frame-Options headers with Flask-Talisman
  - Include security-related headers:
    ```python
    # app.py
    from flask_talisman import Talisman
    
    talisman = Talisman(
        app,
        content_security_policy={
            'default-src': "'self'",
            'script-src': "'self'"
        },
        force_https=True,  # for production
        session_cookie_secure=True,  # for HTTPS sites
        session_cookie_http_only=True
    )
    ```
- **All keys and environment variables must be read from a `.env` file. Use an appropriate library (e.g., `python-dotenv` for Python) to securely load these configurations.**
- **Do NOT hardcode any secrets.**
- Never trust user input; use Flask-WTF for validation:
  ```python
  from flask_wtf import FlaskForm
  from wtforms import StringField, IntegerField, validators
  
  class UserInputForm(FlaskForm):
      name = StringField('Name', [validators.Length(min=1, max=100)])
      email = StringField('Email', [validators.Email()])
      age = IntegerField('Age', [validators.NumberRange(min=0, max=120)])
      
      def validate_name(form, field):
          """Custom validation for name field"""
          # Custom validation logic
          pass
  ```

## Default Tech Stack
- **Python 3.9+**: For backend logic and scripting.
- **Flask 2.0+**: For web framework and REST API.
  - Flask-RESTful for API development
  - Flask-SQLAlchemy for ORM
  - Flask-Migrate for database migrations
  - Flask-WTF for forms and CSRF protection
  - Flask-Login for authentication
  - Flask-Admin for admin interfaces
- **PostgreSQL/SQLite**: PostgreSQL for production, SQLite for development.
- **Frontend**:
  - Chart.js: For data visualization.
  - jQuery 3.x: For DOM manipulation and AJAX requests.
  - Bootstrap 5: For responsive design and UI components.
  - ES6+ JavaScript: Modern JavaScript syntax with optional TypeScript
- **Testing**:
  - pytest: For efficient test running
  - pytest-flask: For Flask-specific testing utilities
  - factory-boy: For test data generation
  - coverage: For measuring test coverage
- **Development Tools**:
  - Docker/Docker Compose: For consistent development environments
  - pre-commit hooks: For code quality checking
  - black/flake8/isort: For code formatting and linting

## Coding Style and Best Practices
- **Follow PEP 8**: Python code should follow PEP 8 style guide
- **Modularity**: Write modular code that is easier to maintain and test.
- **DRY (Don't Repeat Yourself)**: Reuse code when possible through inheritance and composition.
- **Consistency**: Follow consistent naming conventions and coding standards.
- **Flask-specific conventions**:
  - Use blueprints for logical modules
  - Use application factories for flexible instantiation
  - Keep routes short and focused
  - Use view functions for small applications and class-based views for larger ones
- **Error Handling**: Implement robust exception handling with appropriate error messages.
- **Comments and Documentation**:
  - Use docstrings for classes and methods
  - Comment complex algorithms and logic
  - Use type hints consistently