#!/bin/bash
# Setup environment for XGBoost and other ML libraries

export PATH="$HOME/.homebrew/bin:$PATH"
export DYLD_LIBRARY_PATH="$HOME/.homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH"

echo "✅ Environment configured for XGBoost"
echo "   PATH: $PATH"
echo "   DYLD_LIBRARY_PATH: $DYLD_LIBRARY_PATH"
