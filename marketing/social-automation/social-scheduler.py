#!/usr/bin/env python3
"""
PM33 Social Media Automation Scheduler
Multi-platform social media automation with Claude-generated content
"""

import os
import json
import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List
import anthropic
from dotenv import load_dotenv

load_dotenv()

class SocialScheduler:
    def __init__(self):
        self.claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.platforms = {
            'linkedin': {'max_chars': 3000, 'optimal_chars': 1300},
            'twitter': {'max_chars': 280, 'optimal_chars': 240},
            'reddit': {'max_chars': 40000, 'optimal_chars': 1500}
        }
        self.content_queue = []
        self.posting_times = {
            'linkedin': ['09:00', '12:00', '17:00'],  # Business hours
            'twitter': ['08:00', '12:00', '15:00', '18:00'],  # High engagement
            'reddit': ['10:00', '14:00', '20:00']  # Community active times
        }
        
    def generate_platform_content(self, base_topic: str, platform: str, content_type: str = "thought_leadership") -> Dict:
        """Generate platform-specific content"""
        platform_specs = self.platforms[platform]
        
        content_types = {
            "thought_leadership": "Share insights on PM trends and best practices",
            "product_feature": "Highlight PM33 capabilities and benefits", 
            "community_engagement": "Ask questions to engage PM community",
            "case_study": "Share customer success stories",
            "industry_news": "Comment on relevant product management news",
            "tips_tricks": "Share actionable PM tips and workflows"
        }
        
        content_focus = content_types.get(content_type, content_types["thought_leadership"])
        
        prompt = f"""
        Create {platform} content about: {base_topic}
        
        Content type: {content_type} - {content_focus}
        
        Platform requirements:
        - Platform: {platform}
        - Optimal length: {platform_specs['optimal_chars']} characters
        - Max length: {platform_specs['max_chars']} characters
        
        Platform-specific guidelines:
        LinkedIn: Professional tone, industry insights, thought leadership
        Twitter: Conversational, trending hashtags, concise insights  
        Reddit: Helpful, community-focused, avoid self-promotion
        
        Requirements:
        - Native to platform (not obviously cross-posted)
        - Include relevant hashtags
        - Clear value for audience
        - Subtle PM33 positioning (when appropriate)
        - Include engagement hook (question, poll, etc.)
        
        For {platform}, focus on what resonates with product managers on this platform.
        """
        
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "platform": platform,
            "content": response.content[0].text,
            "topic": base_topic,
            "type": content_type,
            "char_count": len(response.content[0].text),
            "generated_at": datetime.now().isoformat(),
            "scheduled_for": None
        }
    
    def create_content_series(self, theme: str, num_posts: int = 5) -> List[Dict]:
        """Create a series of related posts across platforms"""
        series_topics = self.generate_series_topics(theme, num_posts)
        content_series = []
        
        for i, topic in enumerate(series_topics):
            # Rotate content types
            content_types = ["thought_leadership", "tips_tricks", "community_engagement", "case_study", "industry_news"]
            content_type = content_types[i % len(content_types)]
            
            # Create content for each platform
            for platform in self.platforms.keys():
                content = self.generate_platform_content(topic, platform, content_type)
                content['series'] = theme
                content['series_position'] = i + 1
                content_series.append(content)
        
        return content_series
    
    def generate_series_topics(self, theme: str, num_posts: int) -> List[str]:
        """Generate related topics for a content series"""
        prompt = f"""
        Create {num_posts} specific topics for a {theme} content series for product managers.
        
        Series theme: {theme}
        
        Requirements:
        - Each topic should be specific and actionable
        - Build on each other logically
        - Mix educational and practical content
        - Relevant to product management challenges
        - Good for social media engagement
        
        Output format: Just list the {num_posts} topics, one per line.
        """
        
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        
        topics = [line.strip() for line in response.content[0].text.split('\n') if line.strip()]
        return topics[:num_posts]
    
    def schedule_content_series(self, content_series: List[Dict], start_date: datetime = None) -> List[Dict]:
        """Schedule content series across platforms with optimal timing"""
        if not start_date:
            start_date = datetime.now()
        
        scheduled_content = []
        current_date = start_date
        
        # Group content by platform
        platform_content = {}
        for content in content_series:
            platform = content['platform']
            if platform not in platform_content:
                platform_content[platform] = []
            platform_content[platform].append(content)
        
        # Schedule each platform's content
        for platform, posts in platform_content.items():
            posting_times = self.posting_times[platform]
            time_index = 0
            
            for i, post in enumerate(posts):
                # Calculate posting date (spread posts over days)
                days_offset = i // len(posting_times)
                post_date = current_date + timedelta(days=days_offset)
                
                # Get optimal posting time for this platform
                post_time = posting_times[time_index % len(posting_times)]
                post_datetime = post_date.replace(
                    hour=int(post_time.split(':')[0]),
                    minute=int(post_time.split(':')[1]),
                    second=0,
                    microsecond=0
                )
                
                post['scheduled_for'] = post_datetime.isoformat()
                scheduled_content.append(post)
                time_index += 1
        
        return scheduled_content
    
    def generate_engagement_responses(self, original_post: str, engagement_type: str, context: str = "") -> str:
        """Generate responses for social media engagement"""
        prompt = f"""
        Generate a response for social media engagement:
        
        Original post: {original_post}
        Engagement type: {engagement_type} (comment, reply, share_comment)
        Context: {context}
        
        Requirements:
        - Professional but personable tone
        - Add value to the conversation
        - Subtle thought leadership
        - Encourage further discussion
        - Keep it concise (under 200 characters for most platforms)
        
        Engagement guidelines:
        - Comment: Insightful addition to the discussion
        - Reply: Direct response to someone's comment
        - Share comment: Add context when sharing others' content
        """
        
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def analyze_post_performance(self, post_data: Dict) -> Dict:
        """Analyze social media post performance and suggest improvements"""
        prompt = f"""
        Analyze this social media post performance:
        
        Platform: {post_data.get('platform', 'Unknown')}
        Content: {post_data.get('content', 'No content')[:200]}...
        Engagement metrics:
        - Likes: {post_data.get('likes', 0)}
        - Comments: {post_data.get('comments', 0)}
        - Shares: {post_data.get('shares', 0)}
        - Reach: {post_data.get('reach', 0)}
        - Click-through rate: {post_data.get('ctr', 0)}%
        
        Provide analysis:
        1. Performance assessment (Poor/Good/Excellent)
        2. What worked well
        3. Areas for improvement
        4. Suggestions for similar future posts
        5. Optimal posting time recommendations
        
        Keep analysis concise and actionable.
        """
        
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "post_id": post_data.get('id', 'unknown'),
            "analysis": response.content[0].text,
            "analyzed_at": datetime.now().isoformat()
        }

# Content automation scheduler
def run_daily_content_automation():
    """Daily automated content generation and scheduling"""
    scheduler = SocialScheduler()
    
    # Weekly themes for consistent content planning
    weekly_themes = [
        "AI in Product Management",
        "Product Discovery Techniques", 
        "Agile and PM Best Practices",
        "Product Metrics and Analytics",
        "Stakeholder Management",
        "Product Strategy and Vision",
        "User Research and Validation"
    ]
    
    current_week = datetime.now().isocalendar()[1]
    theme = weekly_themes[current_week % len(weekly_themes)]
    
    # Generate and schedule content series
    content_series = scheduler.create_content_series(theme, 5)
    scheduled_content = scheduler.schedule_content_series(content_series)
    
    # Save to content queue
    with open('scheduled_content.json', 'w') as f:
        json.dump(scheduled_content, f, indent=2, default=str)
    
    print(f"Generated and scheduled {len(scheduled_content)} posts for theme: {theme}")

if __name__ == "__main__":
    # Test the automation
    scheduler = SocialScheduler()
    
    # Generate sample content
    linkedin_content = scheduler.generate_platform_content(
        "How AI is transforming product roadmap prioritization",
        "linkedin", 
        "thought_leadership"
    )
    
    print(f"Generated LinkedIn content: {linkedin_content['char_count']} characters")
    print(linkedin_content['content'][:100] + "...")
    
    # Schedule daily automation
    schedule.every().day.at("08:00").do(run_daily_content_automation)
    
    print("Social automation scheduler ready. Run daily content generation at 8 AM.")