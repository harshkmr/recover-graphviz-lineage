FROM python:3.12-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    graphviz \
    tmux \
    asciinema \
    && rm -rf /var/lib/apt/lists/*

# Install Terraform
RUN curl -LO https://releases.hashicorp.com/terraform/1.9.0/terraform_1.9.0_linux_amd64.zip \
    && unzip terraform_1.9.0_linux_amd64.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform_1.9.0_linux_amd64.zip

# Install Python packages
RUN python -m pip install --no-cache-dir \
    pytest==8.4.1 \
    pytest-json-ctrf==0.3.5 \
    pandas \
    datasets \
    huggingface_hub

# Pre-cache the Hugging Face dataset (dair-ai/emotion)
RUN python -c "from datasets import load_dataset; load_dataset('dair-ai/emotion')"

# Enforce offline mode for the agent
ENV HF_HUB_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1

WORKDIR /app
