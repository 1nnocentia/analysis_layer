# base image
FROM python:3.10-slim

# working directory
WORKDIR /app

# instal git dan library
RUN apt-get update && apt-get install -y git build-essential

# manajemen versi solidity
RUN pip install solc-select

# atur versi
RUN solc-select install 0.8.20 && solc-select use 0.8.20