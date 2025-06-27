FROM python:3.11-bullseye

# Set the working directory
WORKDIR /app/backend

# First copy requirements to leverage Docker cache
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN python -m pip install gunicorn

# Copy the backend code
COPY . .

# Set environment variable for Python path
ENV PYTHONPATH=/app/backend

# Start gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "main:app"]
