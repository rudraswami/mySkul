import requests
import json

# Login first
login_data = {
    "email": "test@dhruvai.com",
    "password": "password123"
}

login_response = requests.post(
    "https://study-streak-app.preview.emergentagent.com/api/auth/login",
    json=login_data
)

if login_response.status_code == 200:
    token = login_response.json()['token']
    
    # Test study plan
    study_plan_data = {
        "target_exam_date": "2025-05-15T00:00:00Z",
        "daily_study_hours": 6,
        "weak_subjects": ["Mathematics", "Physics"],
        "strong_subjects": ["Chemistry"],
        "preferred_study_times": ["morning", "evening"],
        "stress_level": 7
    }
    
    response = requests.post(
        "https://study-streak-app.preview.emergentagent.com/api/ai/dual-study-plan",
        json=study_plan_data,
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("Study Plan Response:")
        print(json.dumps(data, indent=2))
        
        # Check dual intelligence structure
        dual_plan = data.get('dual_intelligence_plan', {})
        professor_plan = dual_plan.get('professor', {})
        mentor_plan = dual_plan.get('mentor', {})
        
        print(f"\nProfessor academic_structure length: {len(professor_plan.get('academic_structure', ''))}")
        print(f"Mentor personalized_guidance length: {len(mentor_plan.get('personalized_guidance', ''))}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
else:
    print(f"Login failed: {login_response.status_code} - {login_response.text}")