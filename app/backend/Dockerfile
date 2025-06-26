FROM python:3.11-bullseye

# Set the working directory
WORKDIR /app

# First copy requirements to leverage Docker cache
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN python -m pip install gunicorn

# Copy the backend code
COPY . .

# Set environment variable for Python path
ENV PYTHONPATH=/app

# Start gunicorn from the directory where main.py and app.py are located
CMD ["gunicorn", "--config", "gunicorn.conf.py", "main:app"]
