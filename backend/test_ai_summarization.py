import sys
import os
import time
import fitz  # PyMuPDF

sys.path.append('.')

from app.utils.model_handler import ModelHandler

# Sample employment contract text

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Load sample contract text from PDF
sample_contract = extract_text_from_pdf("sample_employment_contract_1.pdf")

def test_ai_summarization():
    print("🤖 Testing AI-Powered Employment Contract Summarization")
    print("=" * 60)

    # Initialize model handler
    print("🔧 Initializing AI model...")
    start_time = time.time()

    try:
        model_handler = ModelHandler()
        init_time = time.time() - start_time
        print(f"✅ Model initialized in {init_time:.1f} seconds")

        if not model_handler.is_model_loaded():
            print("❌ AI model failed to load - check dependencies")
            return

    except Exception as e:
        print(f"❌ Failed to initialize model: {e}")
        return

    # Create output directory
    output_dir = "summaries"
    os.makedirs(output_dir, exist_ok=True)

    # Test different summary types
    summary_types = [
        ('brief', 150),
        ('standard', 250),
        ('detailed', 2000)
    ]

    print(f"\n📄 Original contract length: {len(sample_contract.split())} words")
    print("=" * 60)

    for summary_type, max_length in summary_types:
        print(f"\n🎯 Generating {summary_type.upper()} summary (max {max_length} words)...")

        start_time = time.time()

        try:
            result = model_handler.generate_summary(sample_contract, max_length)
            generation_time = time.time() - start_time

            summary_text = result['summary']
            summary_words = len(summary_text.split())
            confidence = result.get('confidence', 'N/A')
            model_used = result.get('model_used', 'Unknown')

            print(f"✅ {summary_type.title()} Summary Generated:")
            print(f"   ⏱️  Generation Time: {generation_time:.1f} seconds")
            print(f"   🤖 Model Used: {model_used}")
            print(f"   📊 Confidence: {confidence}")
            print(f"   📏 Length: {summary_words} words")

            # Save to file
            filename = os.path.join(output_dir, f"{summary_type}_summary.txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# {summary_type.title()} Summary\n")
                f.write(f"- Model Used: {model_used}\n")
                f.write(f"- Generation Time: {generation_time:.1f} seconds\n")
                f.write(f"- Confidence: {confidence}\n")
                f.write(f"- Word Count: {summary_words}\n\n")
                f.write(summary_text)

            print(f"📁 Summary saved to: {filename}")

            # Check for warnings
            if summary_words > max_length * 1.2:
                print(f"⚠️  Warning: Summary exceeds target length ({summary_words} > {max_length})")
            if confidence != 'N/A' and confidence < 0.6:
                print(f"⚠️  Warning: Low confidence score ({confidence})")

        except Exception as e:
            print(f"❌ Error generating {summary_type} summary: {e}")

    print("\n" + "=" * 60)
    print("🎉 AI Summarization test completed!")
    print("\n💡 Tips for better results:")
    print("   - Ensure employment contracts have clear section headers")
    print("   - Include key information like salary, position, and terms")
    print("   - Use standard employment contract language")


def test_model_components():
    """Test individual model components"""
    print("\n🔬 Testing Model Components...")

    try:
        from transformers import T5Tokenizer, T5ForConditionalGeneration
        import torch

        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"✅ CUDA available: {torch.cuda.is_available()}")
        print(f"✅ Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")

        tokenizer = T5Tokenizer.from_pretrained('t5-small')
        tokens = tokenizer.encode("summarize: This is a test employment contract.", return_tensors='pt')
        print(f"✅ Tokenizer working: {len(tokens[0])} tokens generated")

        model = T5ForConditionalGeneration.from_pretrained('t5-small')
        print(f"✅ Model loaded: {model.__class__.__name__}")

        print("✅ All AI components working correctly!")

    except Exception as e:
        print(f"❌ Component test failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting AI Summarization Tests...\n")

    test_model_components()
    test_ai_summarization()

    print("\n🎯 Test complete! If all tests pass, your AI summarization is ready!")
