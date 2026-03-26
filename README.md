# Smart Earthquake News

A comprehensive earthquake monitoring and news application that provides real-time information about seismic activities. This project consists of a FastAPI backend to fetch and serve data, and a Vue.js frontend for an interactive map and list view.

## 🚀 Features

- **Real-time Earthquake Data**: Fetches data from reliable sources.
- **Interactive Map**: View earthquake locations on an interactive Leaflet map.
- **News Feed**: Displays the latest news related to seismic events.
- **Dockerized Environment**: Easily deployable using Docker and Docker Compose.
- **API Support**: Clean FastAPI backend serving structured data.

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **ORM/Migration**: [Alembic](https://alembic.sqlalchemy.org/)
- **Containerization**: [Docker](https://www.docker.com/)

### Frontend
- **Framework**: [Vue 3](https://vuejs.org/) (Composition API)
- **Tooling**: [Vite](https://vitejs.dev/)
- **Styling**: Vanilla CSS / Responsive Design
- **Maps**: [Leaflet](https://leafletjs.com/)

---

## 📂 Project Structure

```text
├── fastAPI/             # Python FastAPI Backend
│   ├── main.py          # API Entry point
│   ├── model/           # Database Models
│   ├── repository/      # Data access layer
│   ├── services/        # Business logic
│   └── requirements.txt # Python dependencies
├── frontend/            # Vue.js Frontend
│   ├── src/             # Source files (components, views, assets)
│   ├── public/          # Static assets
│   └── package.json     # Node.js dependencies
├── docker-compose.yml   # Docker configuration
└── README.md            # Project documentation
```

---

## 🏁 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) & [Docker Compose](https://docs.docker.com/compose/install/)
- (Optional for manual setup) [Python 3.10+](https://www.python.org/) & [Node.js 20+](https://nodejs.org/)

### 🐳 Using Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd smart-earthquake-news
   ```

2. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - **Frontend**: http://localhost
   - **Backend API**: http://localhost:8000
   - **API Docs (Swagger)**: http://localhost:8000/docs

### 💻 Manual Setup

#### Backend (fastAPI)
1. Navigate to the `fastAPI` directory:
   ```bash
   cd fastAPI
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables (copy `.env.example` to `.env`).
5. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

#### Frontend (frontend)
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Configure environment variables (VITE_API_URL).
4. Run the development server:
   ```bash
   npm run dev
   ```

---

## ⚙️ Environment Variables

### Backend (`fastAPI/.env`)
| Variable | Description | Default |
|----------|-------------|---------|
| `DB_USER` | PostgreSQL Username | `postgres` |
| `DB_PASSWORD` | PostgreSQL Password | `postgres` |
| `DB_HOST` | Database Host | `localhost` / `db` |
| `DB_NAME` | Database Name | `smart_news` |
| `USE_API` | Fetch from live API | `TRUE` |

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
