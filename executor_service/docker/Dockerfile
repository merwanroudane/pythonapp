# Runtime images for the Docker execution backend (blueprint §103.3 runtime profiles).
#
#   docker build -f executor_service/docker/Dockerfile --target core-python -t pll-runner:core .
#   docker build -f executor_service/docker/Dockerfile --target scientific  -t pll-runner:scientific .
#
# Containers are started read-only, without network, as uid 65534, with all
# capabilities dropped (see app/execution/docker_backend.py).

FROM python:3.11-slim AS core-python
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONUTF8=1
COPY app/execution/harness.py /opt/pll/harness.py
USER 65534:65534
WORKDIR /work

FROM core-python AS scientific
USER root
RUN pip install --no-cache-dir "numpy>=2" "pandas>=2.2" "matplotlib>=3.9" "pillow>=10" \
    && rm -rf /root/.cache
USER 65534:65534
