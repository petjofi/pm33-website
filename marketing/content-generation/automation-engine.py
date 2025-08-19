#!/usr/bin/env python3
"""
PM33 Marketing Content Generation Engine
Automates content creation across all channels using Claude API
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List
import anthropic
from dotenv import load_dotenv

load_dotenv()

class ContentEngine:
    def __init__(self):
        self.claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.content_calendar = {}
        
    def generate_blog_post(self, topic: str, keywords: List[str], target_audience: str = "Product Managers") -> Dict:
        """Generate SEO-optimized blog post"""
        prompt = f"""
        Create a high-quality blog post about {topic} for PM33's audience of {target_audience}.
        
        Target keywords: {', '.join(keywords)}
        
        Requirements:
        - 1500-2000 words
        - SEO optimized with keywords naturally integrated
        - Include industry insights and practical tips
        - Position PM33 as the AI-native solution
        - Include clear CTAs for trial signup
        - Use engaging subheadings and bullet points
        
        Structure:
        1. Hook opening with pain point
        2. 3-4 main sections with actionable insights
        3. PM33 solution integration (subtle, not salesy)
        4. Strong CTA to trial
        
        Output format: Title, meta description, full article content
        """
        
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        return {
            "type": "blog_post",
            "topic": topic,
            "keywords": keywords,
            "content": content,
            "created_at": datetime.now().isoformat()
        }
    
    def generate_social_content(self, platform: str, base_content: str, call_to_action: str) -> Dict:
        """Generate platform-specific social media content"""
        platform_specs = {
            "linkedin": {"max_length": 1300, "style": "professional, thought leadership"},
            "twitter": {"max_length": 280, "style": "concise, engaging"},
            "reddit": {"max_length": 10000, "style": "helpful, community-focused"}
        }
        
        spec = platform_specs.get(platform, platform_specs["linkedin"])
        
        prompt = f"""
        Adapt this content for {platform}:
        
        Base content: {base_content[:500]}...
        
        Platform requirements:
        - Max length: {spec['max_length']} characters
        - Style: {spec['style']}
        - Include relevant hashtags
        - Strong CTA: {call_to_action}
        
        Make it native to the platform while maintaining PM33's value proposition.
        """
        
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "platform": platform,
            "content": response.content[0].text,
            "cta": call_to_action,
            "created_at": datetime.now().isoformat()
        }
    
    def generate_email_sequence(self, lead_profile: Dict, sequence_length: int = 5) -> List[Dict]:
        """Generate personalized email nurture sequence"""
        sequence = []
        
        for day in [1, 3, 7, 14, 21][:sequence_length]:
            prompt = f"""
            Create email #{len(sequence) + 1} for a {sequence_length}-email nurture sequence.
            
            Lead profile:
            - Role: {lead_profile.get('role', 'Product Manager')}
            - Company: {lead_profile.get('company', 'Unknown')}
            - Pain point: {lead_profile.get('pain_point', 'Manual PM processes')}
            - Company size: {lead_profile.get('company_size', '50-200 employees')}
            
            Email context:
            - Day {day} of nurture sequence
            - Focus: Education and value, not selling
            - Include relevant PM33 benefits
            - Strong but soft CTA
            
            Output: Subject line and email body (300-400 words)
            """
            
            response = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            sequence.append({
                "day": day,
                "content": response.content[0].text,
                "lead_profile": lead_profile,
                "created_at": datetime.now().isoformat()
            })
        
        return sequence

if __name__ == "__main__":
    engine = ContentEngine()
    
    # Test blog generation
    blog = engine.generate_blog_post(
        "AI-Powered Product Roadmapping", 
        ["AI product management", "product roadmap automation", "AI roadmap tools"],
        "Senior Product Managers"
    )
    print("Blog generated:", blog["topic"])