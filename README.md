# Artist Management System

This is a web-based **Artist Management System** that allows you to manage artists, music records, and users. It includes features like adding, editing, and deleting artists and music records, as well as uploading CSV files to bulk-import music data.

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.8+**
- **pip** (Python package manager)
- **Virtualenv** (for creating a virtual environment)

---

## Setup Instructions

Follow these steps to set up and run the project locally.

### 1. Clone the Repository

Clone the project repository to your local machine:

```bash
git clone https://github.com/merin31/silver-eureka.git
cd silver-eureka/

virtualenv venv
source venv/bin/activate
```

### 2. Setup Environment
for linux
```bash
virutalenv venv

source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run migrations
```bash
python migrate.py
```
### 4. Run the Application
```bash
python main.py
```


