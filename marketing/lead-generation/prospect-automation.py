#!/usr/bin/env python3
"""
PM33 Lead Generation and Prospect Automation
Identifies, qualifies, and nurtures prospects automatically
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List
import anthropic
from dotenv import load_dotenv

load_dotenv()

class ProspectAutomation:
    def __init__(self):
        self.claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.qualified_prospects = []
        
    def analyze_prospect(self, prospect_data: Dict) -> Dict:
        """Use AI to qualify and score prospects"""
        prompt = f"""
        Analyze this prospect for PM33 (AI-native product management platform):
        
        Prospect data:
        - Name: {prospect_data.get('name', 'Unknown')}
        - Role: {prospect_data.get('role', 'Unknown')}
        - Company: {prospect_data.get('company', 'Unknown')}
        - Company size: {prospect_data.get('company_size', 'Unknown')}
        - Industry: {prospect_data.get('industry', 'Unknown')}
        - Current tools: {prospect_data.get('current_tools', 'Unknown')}
        - Pain points: {prospect_data.get('pain_points', 'Unknown')}
        
        Provide analysis:
        1. Lead score (0-100): Based on fit for PM33
        2. Qualification level: Cold/Warm/Hot
        3. Best approach: Email/LinkedIn/Demo request
        4. Key pain points to address
        5. Personalization angles
        6. Recommended next steps
        
        PM33 ideal customer: Mid-market to enterprise companies (50-5000 employees), 
        product teams using Jira/Asana/Monday, struggling with manual PM processes,
        looking for AI automation.
        """
        
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis = response.content[0].text
        
        # Extract lead score (simplified parsing)
        lead_score = 50  # Default
        if "Lead score" in analysis:
            try:
                score_line = [line for line in analysis.split('\n') if 'Lead score' in line][0]
                lead_score = int(''.join(filter(str.isdigit, score_line.split(':')[1])))
            except:
                pass
        
        return {
            "prospect_id": f"{prospect_data.get('company', '')}-{prospect_data.get('name', '')}".replace(' ', '-').lower(),
            "analysis": analysis,
            "lead_score": lead_score,
            "analyzed_at": datetime.now().isoformat(),
            "prospect_data": prospect_data
        }
    
    def generate_personalized_outreach(self, prospect_analysis: Dict, channel: str = "linkedin") -> Dict:
        """Generate personalized outreach message"""
        prospect_data = prospect_analysis["prospect_data"]
        analysis = prospect_analysis["analysis"]
        
        prompt = f"""
        Create a personalized {channel} outreach message for this prospect:
        
        Prospect: {prospect_data.get('name')} at {prospect_data.get('company')}
        Role: {prospect_data.get('role')}
        
        Analysis insights: {analysis[:500]}...
        
        Message requirements:
        - Personal and relevant (not obviously templated)
        - Lead with value, not pitch
        - Reference specific pain points from analysis
        - Soft CTA (valuable resource or quick question)
        - Professional but conversational tone
        - {channel}-appropriate length and format
        
        For LinkedIn: Keep under 300 characters for connection request, 
        or 1000 characters for direct message.
        
        Include suggested follow-up sequence if they respond positively.
        """
        
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "prospect_id": prospect_analysis["prospect_id"],
            "channel": channel,
            "message": response.content[0].text,
            "generated_at": datetime.now().isoformat()
        }
    
    def create_prospect_nurture_plan(self, prospect_analysis: Dict) -> List[Dict]:
        """Create multi-touch nurture plan based on prospect analysis"""
        lead_score = prospect_analysis["lead_score"]
        prospect_data = prospect_analysis["prospect_data"]
        
        # Customize nurture intensity based on lead score
        if lead_score >= 80:
            # Hot leads: Aggressive nurture
            touchpoints = [
                {"day": 0, "type": "linkedin_connect", "priority": "high"},
                {"day": 1, "type": "linkedin_message", "priority": "high"},
                {"day": 3, "type": "demo_invite", "priority": "high"},
                {"day": 7, "type": "follow_up_email", "priority": "medium"},
                {"day": 14, "type": "case_study_share", "priority": "medium"}
            ]
        elif lead_score >= 60:
            # Warm leads: Moderate nurture
            touchpoints = [
                {"day": 0, "type": "linkedin_connect", "priority": "medium"},
                {"day": 3, "type": "value_content_share", "priority": "medium"},
                {"day": 7, "type": "linkedin_message", "priority": "medium"},
                {"day": 14, "type": "demo_invite", "priority": "low"}
            ]
        else:
            # Cold leads: Light nurture
            touchpoints = [
                {"day": 0, "type": "linkedin_connect", "priority": "low"},
                {"day": 7, "type": "value_content_share", "priority": "low"},
                {"day": 21, "type": "re_engagement", "priority": "low"}
            ]
        
        # Generate specific content for each touchpoint
        nurture_plan = []
        for touchpoint in touchpoints:
            content = self.generate_touchpoint_content(
                prospect_data, 
                touchpoint["type"], 
                touchpoint["day"]
            )
            
            nurture_plan.append({
                "day": touchpoint["day"],
                "type": touchpoint["type"],
                "priority": touchpoint["priority"],
                "content": content,
                "prospect_id": prospect_analysis["prospect_id"]
            })
        
        return nurture_plan
    
    def generate_touchpoint_content(self, prospect_data: Dict, touchpoint_type: str, day: int) -> str:
        """Generate specific content for each nurture touchpoint"""
        prompt = f"""
        Create {touchpoint_type} content for day {day} of prospect nurture:
        
        Prospect: {prospect_data.get('name')} at {prospect_data.get('company')}
        Role: {prospect_data.get('role')}
        
        Touchpoint type: {touchpoint_type}
        - linkedin_connect: Connection request message
        - linkedin_message: Direct LinkedIn message
        - demo_invite: Demo invitation with calendar link
        - value_content_share: Share valuable content/resource
        - case_study_share: Share relevant customer success story
        - follow_up_email: Email follow-up
        - re_engagement: Re-engagement attempt
        
        Keep it brief, personal, and value-focused.
        """
        
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text

if __name__ == "__main__":
    automation = ProspectAutomation()
    
    # Test prospect analysis
    test_prospect = {
        "name": "Sarah Johnson",
        "role": "Senior Product Manager",
        "company": "TechCorp",
        "company_size": "200-500",
        "industry": "SaaS",
        "current_tools": "Jira, Confluence",
        "pain_points": "Manual roadmap updates, lack of stakeholder visibility"
    }
    
    analysis = automation.analyze_prospect(test_prospect)
    print(f"Lead score: {analysis['lead_score']}")
    
    outreach = automation.generate_personalized_outreach(analysis, "linkedin")
    print(f"Outreach generated for: {test_prospect['name']}")
    
    nurture_plan = automation.create_prospect_nurture_plan(analysis)
    print(f"Nurture plan: {len(nurture_plan)} touchpoints")