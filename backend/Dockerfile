FROM python:3.8-slim-buster

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set work directory
WORKDIR /app/backend
# Install dependencies
COPY Pipfile Pipfile.lock /app/backend/
RUN pip install pipenv && pipenv install --system
# Copy project
COPY . /app/backend/
# EXPOSE 8000
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000","--noreload"]