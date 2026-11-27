FROM python:3.12-slim
WORKDIR /app
COPY control-center/ /app/
RUN python -m py_compile agent_api.py
USER 65534:65534
EXPOSE 8080
CMD ["python", "agent_api.py"]
