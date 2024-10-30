# Django Project Setup

## Prerequisites

- Python (version 3.x)
- `pip` (Python package installer)
- Git (optional, if you're cloning the repository)

---
## Setting up the Development Environment

# 1. Clone the Repository 

```bash
git clone https://github.com/sravaniSuravarapu/audvik_assignment.git
cd yourrepository

2. Create a Virtual Environment
For Windows:

    Open Command Prompt or PowerShell.

    Run the following commands:

bash

# Navigate to your project directory (ASSIGNMENT)
cd yourrepository

# Create a virtual environment
python -m venv env

# Activate the virtual environment
.\env\Scripts\activate

For Linux / macOS:

    Open a terminal.

    Run the following commands:

bash

# Navigate to your project directory (if not already there)
cd yourrepository

# Create a virtual environment
python3 -m venv env

# Activate the virtual environment
source env/bin/activate

3. Install the Requirements

After activating the virtual environment, install the required packages using pip:

bash

pip install -r requirements.txt

Running the Django Project

After installing the requirements, run the following commands to start the Django development server:

bash

# Apply database migrations
python manage.py migrate

# Run the server
python manage.py runserver

Now, your Django application should be running at http://127.0.0.1:8000/!
Deactivating the Virtual Environment





