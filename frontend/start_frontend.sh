#!/bin/bash
cd /app/frontend
export PATH="/usr/local/bin:$PATH"
yarn dev --host 0.0.0.0 --port 3001