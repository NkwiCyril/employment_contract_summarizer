# fix_sentencepiece.sh
# Fix SentencePiece installation for T5 tokenizer

echo "🔧 Fixing SentencePiece installation..."

# Activate virtual environment
source venv/bin/activate

# Install SentencePiece
echo "📦 Installing SentencePiece..."
pip install sentencepiece==0.1.99

# Install protobuf (sometimes needed)
echo "📦 Installing protobuf..."
pip install protobuf==4.25.1

# Alternative: Install specific transformers tokenizers
echo "📦 Installing tokenizers..."
pip install tokenizers==0.20.0

# Test the installation
echo "🧪 Testing SentencePiece installation..."
python -c "
try:
    import sentencepiece
    print('✅ SentencePiece installed successfully!')
    print(f'   Version: {sentencepiece.__version__}')
except ImportError as e:
    print(f'❌ SentencePiece import failed: {e}')

try:
    from transformers import T5Tokenizer
    tokenizer = T5Tokenizer.from_pretrained('t5-small')
    print('✅ T5Tokenizer working!')
except Exception as e:
    print(f'❌ T5Tokenizer failed: {e}')
"

echo "🎯 SentencePiece fix complete!"