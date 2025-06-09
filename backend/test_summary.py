# test_summary.py
# Script to test if summary generation works

from app.utils.model_handler import ModelHandler

# Sample employment contract text
sample_contract = """
EMPLOYMENT CONTRACT

This Employment Contract is entered into between TechCorp Cameroon Ltd., a company incorporated under the laws of Cameroon (the "Company"), and John Doe (the "Employee").

1. POSITION AND DUTIES
The Employee is appointed as Senior Software Developer, reporting to the Engineering Manager. The Employee shall perform duties including but not limited to:
- Leading software development projects
- Mentoring junior developers
- Collaborating with cross-functional teams
- Ensuring code quality and best practices

2. COMPENSATION
Base Salary: 2,500,000 FCFA per month
Annual Bonus: Performance-based, up to 20% of annual salary
Benefits: Health insurance, transport allowance (150,000 FCFA/month)

3. WORKING CONDITIONS
Working Hours: 40 hours per week, Monday to Friday, 8:00 AM to 5:00 PM
Location: Hybrid arrangement - 3 days office, 2 days remote
Annual Leave: 25 working days

4. TERMINATION
Notice Period: 30 days written notice required from either party
Confidentiality: Employee agrees to maintain confidentiality of proprietary information

Start Date: January 15, 2024
Contract Type: Permanent Employment
Probation Period: 3 months
"""

def test_summary_generation():
    print("🧪 Testing Summary Generation...")
    
    # Initialize model handler
    model_handler = ModelHandler()
    
    # Test different summary types
    summary_types = [
        ('brief', 150),
        ('standard', 250),
        ('detailed', 400)
    ]
    
    for summary_type, max_length in summary_types:
        print(f"\n📝 Generating {summary_type} summary...")
        
        try:
            result = model_handler.generate_summary(sample_contract, max_length)
            
            print(f"✅ {summary_type.title()} Summary Generated:")
            print(f"   Model Used: {result['model_used']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Length: {len(result['summary'].split())} words")
            print(f"   Content Preview: {result['summary'][:100]}...")
            
        except Exception as e:
            print(f"❌ Error generating {summary_type} summary: {e}")
    
    print("\n🎯 Summary generation test completed!")

if __name__ == "__main__":
    test_summary_generation()