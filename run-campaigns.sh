#!/bin/bash

# Zoho Gym Campaigns - One-Click Runner
# This script automatically creates professional email campaigns in Zoho

set -e

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "   ZOHO GYM CAMPAIGNS - PROFESSIONAL EMAIL CREATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if we're in the right directory
if [ ! -f "config.txt" ]; then
    echo "❌ Error: config.txt not found"
    echo "Please run this script from your project folder:"
    echo "   cd ~/Documents/zoho-gym-campaigns"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Install from: https://www.python.org/downloads/"
    exit 1
fi

# Load configuration
echo "📋 Loading configuration..."
export $(grep -v '^#' config.txt | xargs)

# Run the main script
echo "🚀 Starting campaign creation..."
echo ""

python3 main.py

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ DONE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📧 Next steps:"
echo "   1. Log into Zoho Campaigns (https://campaigns.zoho.com.au)"
echo "   2. Check your Drafts folder"
echo "   3. Review the professional email designs"
echo "   4. Edit and customize as needed"
echo "   5. Set send dates and send to your audience"
echo ""
