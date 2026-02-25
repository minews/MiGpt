FROM python:3.12

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY . .

RUN uv sync --no-dev --frozen

ENV XDG_CONFIG_HOME=/config
ENV XIAOGPT_PORT=9527
VOLUME /config
EXPOSE 9527
ENTRYPOINT ["uv", "run", "xiaogpt"]
