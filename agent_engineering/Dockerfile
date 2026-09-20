ARG PYTHON_IMAGE=python:3.11-slim
FROM ${PYTHON_IMAGE}

WORKDIR /app
COPY pyproject.toml README.md ./
COPY app app
COPY agent agent
COPY db db
COPY tools tools
COPY skills skills
COPY eval eval
COPY mock_boh_cli mock_boh_cli

RUN pip install --no-cache-dir .

ENV DATABASE_URL=mysql+pymysql://agent:agent@mysql:3306/agent_interview
ENV MOCK_BOH_STATE=/app/var/mock_bohrium_state.json

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
