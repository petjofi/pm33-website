#!/usr/bin/env python3
"""
Day 3 Content Generation for PM33 Beta User Acquisition
Generates specific content pieces for reaching 50 beta users
"""

import os
import sys
sys.path.append('content-generation')

# Import the content engine from the existing file
import importlib.util
spec = importlib.util.spec_from_file_location("automation_engine", "content-generation/automation-engine.py")
automation_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(automation_engine)
ContentEngine = automation_engine.ContentEngine
from datetime import datetime
import json

def generate_day3_content():
    """Generate all Day 3 marketing content for beta acquisition"""
    engine = ContentEngine()
    
    print("🎯 PM33 Day 3 Content Generation")
    print("Goal: Generate content to acquire 50 beta users")
    print("=" * 60)
    
    # 1. Beta Announcement Blog Post
    print("1️⃣  Generating Beta Announcement Blog Post...")
    beta_blog = engine.generate_blog_post(
        topic="Introducing PM33: The AI Strategic Co-Pilot That Replaces $8,400/Year Consultants", 
        keywords=["AI product management", "strategic consultant", "product manager tools", "AI co-pilot"],
        target_audience="Senior Product Managers at Scale-up Companies"
    )
    
    # Save blog post
    with open('blogs/pm33-beta-announcement.md', 'w') as f:
        f.write(beta_blog['content'])
    print("   ✅ Blog saved to blogs/pm33-beta-announcement.md")
    
    # 2. LinkedIn Beta Launch Post
    print("2️⃣  Generating LinkedIn Beta Launch Post...")
    linkedin_post = engine.generate_social_content(
        platform="linkedin",
        base_content="PM33 is now in beta! We're looking for Senior Product Managers to test our AI Strategic Co-Pilot that replaces expensive strategic consultants with AI-powered guidance that automatically becomes executable workflows.",
        call_to_action="Join our beta program and get strategic AI guidance for free during testing"
    )
    
    with open('linkedin/beta-launch-post.md', 'w') as f:
        f.write(f"# PM33 Beta Launch - LinkedIn Post\n\n{linkedin_post['content']}")
    print("   ✅ LinkedIn post saved to linkedin/beta-launch-post.md")
    
    # 3. Beta User Email Outreach
    print("3️⃣  Generating Beta User Email Sequence...")
    
    # Different PM profiles to target
    pm_profiles = [
        {
            'role': 'Senior Product Manager',
            'company': 'Series B SaaS Startup',
            'pain_point': 'Strategic decision-making without expensive consultants',
            'company_size': '50-150 employees'
        },
        {
            'role': 'Principal Product Manager', 
            'company': 'Series C Fintech Company',
            'pain_point': 'Converting strategic insights into actionable workflows',
            'company_size': '100-300 employees'
        },
        {
            'role': 'Head of Product',
            'company': 'High-growth Healthtech Startup', 
            'pain_point': 'Team strategic alignment and resource allocation',
            'company_size': '75-200 employees'
        }
    ]
    
    email_sequences = {}
    for i, profile in enumerate(pm_profiles):
        profile_name = f"profile_{i+1}_{profile['role'].lower().replace(' ', '_')}"
        sequence = engine.generate_email_sequence(profile, sequence_length=3)
        email_sequences[profile_name] = {
            'profile': profile,
            'emails': sequence
        }
        print(f"   ✅ Email sequence generated for {profile['role']}")
    
    # Save email sequences
    with open('emails/beta-outreach-sequences.json', 'w') as f:
        json.dump(email_sequences, f, indent=2)
    
    # 4. Product Hunt Launch Announcement
    print("4️⃣  Generating Product Hunt Launch Content...")
    ph_content = engine.generate_social_content(
        platform="twitter",
        base_content="We're launching PM33 on Product Hunt! An AI Strategic Co-Pilot that gives Product Managers instant strategic guidance and turns it into executable workflows. No more limited strategic capabilities consultant fees.",
        call_to_action="Support our Product Hunt launch and join the beta"
    )
    
    with open('social/product-hunt-announcement.md', 'w') as f:
        f.write(f"# Product Hunt Launch Announcement\n\n{ph_content['content']}")
    print("   ✅ Product Hunt content saved to social/product-hunt-announcement.md")
    
    print("\n" + "=" * 60)
    print("🎉 Day 3 Content Generation Complete!")
    print("Generated content for:")
    print("  📝 Beta announcement blog post")
    print("  📱 LinkedIn beta launch post") 
    print("  📧 3 targeted email outreach sequences")
    print("  🚀 Product Hunt launch announcement")
    print("\n🎯 Next: Execute outreach to reach 50 beta users!")

if __name__ == "__main__":
    # Create directories if they don't exist
    os.makedirs('blogs', exist_ok=True)
    os.makedirs('linkedin', exist_ok=True)
    os.makedirs('emails', exist_ok=True)
    os.makedirs('social', exist_ok=True)
    
    generate_day3_content()