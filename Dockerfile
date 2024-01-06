# Stage 0 - Building frontend
FROM node:20-alpine as build-stage

WORKDIR /culivert/frontend

# Install dependencies
COPY ./frontend/package*.json ./
RUN npm install

# Build frontend
COPY ./frontend/ ./
RUN npm run build

# Stage 1
FROM python:3.12-alpine
WORKDIR /culivert/backend

# Install python dependencies
COPY ./backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy frontend build
COPY --from=build-stage /culivert/frontend/dist ./
# Copy backend
COPY ./backend .

# Setup environment variables
ENV FLASK_SECRET_KEY="DEBUG_SECRET"
ENV FLASK_ALLOWED_EXTENSIONS='["png","jpg","jpeg","webp"]'
ENV FLASK_UPLOAD_FOLDER="./static/media/"
ENV FLASK_MAX_CONTENT_LENGTH=8000000

# Setup the volumes
VOLUME ["/culivert/backend/static/media"]

# Setup the entrypoint
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]