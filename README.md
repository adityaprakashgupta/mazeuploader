# MazeUploader

A Python application that generates maze puzzles, creates videos, and uploads them to YouTube.

## Features

- Generates maze puzzles of different difficulty levels (Beginner, Medium, Hard)
- Creates videos with countdown timers and solution paths
- Uploads videos to YouTube with AI-generated titles, descriptions, and tags
- Supports multiple YouTube channels with different configurations
- Uses MongoDB to store channel credentials and configuration

## Docker Setup

### Prerequisites

- Docker
- Docker Compose

### Building and Running with Docker

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd MazeUploader
   ```

2. Build and start the Docker container:
   ```bash
   docker-compose up -d
   ```

3. To stop the container:
   ```bash
   docker-compose down
   ```

### Environment Variables

- `MONGO_URI`: MongoDB connection string (required)

### Volumes

- `./output:/app/output`: Maps the local output directory to the container's output directory for storing generated videos

## Manual Setup

### Prerequisites

- Python 3.13 or higher
- MongoDB
- UV package manager (or pip)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd MazeUploader
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   uv pip install -e .
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## Configuration

The application uses MongoDB to store:
- Channel credentials
- Font schemes
- Color schemes
- Video settings (duration, levels, solution position)

Refer to the database/client.py file for more information on database configuration.

## License

[License Information]
