FROM python:3.12-slim
WORKDIR /app
COPY control-center/ /app/
RUN python -m py_compile agent_api.py && useradd -r -u 10001 app
USER app
EXPOSE 8080
CMD ["python", "agent_api.py"]
