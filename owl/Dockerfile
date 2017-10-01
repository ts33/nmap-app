# Use an official Python runtime as a parent image
FROM python:3.6-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# install nmap package
RUN apk --update add nmap && rm -f /var/cache/apk/*

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Define environment variable
ENV FLASK_APP app.py

# Run app.py when the container launches
CMD ["flask", "run", "-p", "5001", "--host=0.0.0.0"]
