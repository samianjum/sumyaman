FROM python:3.10-slim

# Create a non-root user (Hugging Face requirement)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy and install requirements
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install gunicorn

# Copy project files
COPY --chown=user . .

# Hugging Face uses port 7860 by default
EXPOSE 7860

# Start the app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "mobile_app:app"]
