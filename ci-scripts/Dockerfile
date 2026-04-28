FROM jenkins-agent/trixie

RUN apt-get update && \
    apt-get install -y \
				docker.io \
				python3-dev \
				python3-pip \
    && rm -rf /var/lib/apt/lists/*
