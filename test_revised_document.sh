#!/bin/bash
# Test script for revised document download

echo "🧪 Testing Revised Document Download"
echo "===================================="
echo ""

# Find latest review
LATEST_DIR=$(ls -td outputs/*/ | head -1)
echo "📁 Latest review: $LATEST_DIR"

# Extract review_id from directory name
TIMESTAMP=$(basename "$LATEST_DIR" | grep -oE "[0-9]{8}_[0-9]{6}$")
REVIEW_ID="review_$TIMESTAMP"
echo "🆔 Review ID: $REVIEW_ID"
echo ""

# Check if revised_document.txt exists
REVISED_FILE="${LATEST_DIR}revised_document.txt"
if [ -f "$REVISED_FILE" ]; then
    echo "✅ revised_document.txt exists"
    FILE_SIZE=$(wc -c < "$REVISED_FILE" | xargs)
    echo "📊 File size: $FILE_SIZE bytes"
    echo ""
else
    echo "❌ revised_document.txt NOT found"
    echo "ℹ️  This review might not have iterative improvements"
    exit 0
fi

# Test backend endpoint
echo "🌐 Testing backend endpoint..."
HTTP_CODE=$(curl -s -o /tmp/test_download.txt -w "%{http_code}" "http://localhost:8000/api/review/${REVIEW_ID}/download/txt")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Backend endpoint works! (HTTP $HTTP_CODE)"
    DOWNLOAD_SIZE=$(wc -c < /tmp/test_download.txt | xargs)
    echo "📊 Downloaded: $DOWNLOAD_SIZE bytes"
    
    # Compare sizes
    if [ "$FILE_SIZE" = "$DOWNLOAD_SIZE" ]; then
        echo "✅ File sizes match!"
    else
        echo "⚠️  File sizes differ (expected $FILE_SIZE, got $DOWNLOAD_SIZE)"
    fi
    
    # Show first 5 lines
    echo ""
    echo "📄 First 5 lines of downloaded file:"
    echo "-----------------------------------"
    head -5 /tmp/test_download.txt
    echo "-----------------------------------"
    
else
    echo "❌ Backend endpoint failed (HTTP $HTTP_CODE)"
    cat /tmp/test_download.txt
fi

echo ""
echo "✨ Test complete!"
echo ""
echo "📝 To view in browser, open:"
echo "   http://localhost:3000"
echo "   And look for 'Iterative Improvements' section"
