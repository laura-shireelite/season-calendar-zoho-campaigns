#!/bin/bash
set -e

echo "Pushing updated template to GitHub..."
cd ~/Documents/zoho-gym-campaigns
git push origin main

echo "✓ Push successful!"
echo ""
echo "Now generating fresh campaigns with embedded logo..."
source config.txt
python3 main.py

echo "✓ Campaigns generated successfully!"
echo ""
echo "Check Zoho Campaigns for the new draft campaigns with embedded logo."
