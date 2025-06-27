#!/bin/bash
# Script to validate PyInstaller build in clean container

set -e

echo "🐳 Building validation container..."
docker build -f Dockerfile.validate -t dslmodel-validate .

echo ""
echo "📋 Testing executable in clean container..."
echo "============================================"

echo ""
echo "1️⃣ Testing --help command:"
docker run --rm dslmodel-validate

echo ""
echo "2️⃣ Testing status command:"
docker run --rm dslmodel-validate ./setup-evolution-cron status

echo ""
echo "3️⃣ Testing with different user:"
docker run --rm --user nobody dslmodel-validate ./setup-evolution-cron --help

echo ""
echo "4️⃣ Testing in minimal Alpine Linux:"
cat > Dockerfile.alpine << EOF
FROM alpine:latest
RUN apk add --no-cache libc6-compat
COPY dist/setup-evolution-cron /app/setup-evolution-cron
RUN chmod +x /app/setup-evolution-cron
WORKDIR /app
CMD ["./setup-evolution-cron", "--help"]
EOF

docker build -f Dockerfile.alpine -t dslmodel-validate-alpine .
docker run --rm dslmodel-validate-alpine || echo "Note: Alpine test may fail due to glibc differences"

echo ""
echo "5️⃣ Testing file size and dependencies:"
docker run --rm dslmodel-validate sh -c "ls -lh setup-evolution-cron && file setup-evolution-cron"

echo ""
echo "6️⃣ Testing with strace (if available):"
docker run --rm --cap-add SYS_PTRACE --security-opt seccomp=unconfined dslmodel-validate sh -c "apt-get update > /dev/null 2>&1 && apt-get install -y strace > /dev/null 2>&1 && strace -e openat ./setup-evolution-cron --help 2>&1 | grep -E '\.so|\.py' | head -20" || echo "Strace test skipped"

echo ""
echo "✅ Validation complete!"

# Cleanup
rm -f Dockerfile.alpine