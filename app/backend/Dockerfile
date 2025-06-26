FROM python:3.11-bullseye

# Set the working directory to where the backend code will be
WORKDIR /app/backend

# Copy the backend directory contents to the working directory
COPY ./ /app/backend/

RUN python -m pip install -r requirements.txt

RUN python -m pip install gunicorn

# Start gunicorn from the backend directory where main.py and app.py are located
CMD ["gunicorn", "--config", "gunicorn.conf.py", "main:app"]
