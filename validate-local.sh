#!/bin/bash
# Script to validate PyInstaller build locally

set -e

echo "🔍 Validating PyInstaller build locally..."
echo "=========================================="

# Create a temporary directory for testing
TEST_DIR=$(mktemp -d)
echo "📁 Test directory: $TEST_DIR"

# Copy executable to test directory
cp dist/setup-evolution-cron "$TEST_DIR/"
cp evolution_cron.sh "$TEST_DIR/" 2>/dev/null || echo "#!/bin/bash\necho 'Evolution script executed'" > "$TEST_DIR/evolution_cron.sh"
chmod +x "$TEST_DIR/evolution_cron.sh"

echo ""
echo "1️⃣ Testing executable info:"
ls -lh "$TEST_DIR/setup-evolution-cron"
file "$TEST_DIR/setup-evolution-cron"
otool -L "$TEST_DIR/setup-evolution-cron" | head -10

echo ""
echo "2️⃣ Testing in isolated directory:"
cd "$TEST_DIR"
./setup-evolution-cron --help

echo ""
echo "3️⃣ Testing all commands:"
./setup-evolution-cron status
echo ""
./setup-evolution-cron logs || echo "No logs available"

echo ""
echo "4️⃣ Testing with minimal PATH:"
env -i PATH="/usr/bin:/bin" ./setup-evolution-cron --help

echo ""
echo "5️⃣ Testing with no environment:"
env -i ./setup-evolution-cron --help || echo "Note: May fail without basic env vars"

echo ""
echo "6️⃣ Testing script execution:"
./setup-evolution-cron test

echo ""
echo "7️⃣ Checking for bundled Python:"
strings ./setup-evolution-cron | grep -i "python3.1" | head -5 || echo "Python version info not found in strings"

echo ""
echo "8️⃣ Testing size analysis:"
du -sh ./setup-evolution-cron
echo "Sections in executable:"
size ./setup-evolution-cron || echo "Size command not available"

# Cleanup
cd - > /dev/null
rm -rf "$TEST_DIR"

echo ""
echo "✅ Local validation complete!"