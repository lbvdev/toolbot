FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml uv.lock ./

RUN uv sync --no-dev

COPY . .

CMD ["uv", "run", "python", "-m", "bot.app"]