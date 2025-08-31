#!/usr/bin/env node

// Test script for website analysis functionality
// Tests the enhanced AI prompting with actual content fetching

async function testWebsiteAnalysis(url) {
  console.log(`\n🧪 Testing website analysis for: ${url}`);
  
  try {
    // First, fetch the actual website content (like our enhanced API does)
    let websiteContent = '';
    try {
      console.log('📥 Fetching website content...');
      const websiteResponse = await fetch(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; PM33Bot/1.0)',
        },
        timeout: 10000
      });
      
      if (websiteResponse.ok) {
        const html = await websiteResponse.text();
        // Extract text content from HTML (basic parsing)
        websiteContent = html
          .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '') // Remove scripts
          .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '') // Remove styles
          .replace(/<[^>]+>/g, ' ') // Remove HTML tags
          .replace(/\s+/g, ' ') // Normalize whitespace
          .substring(0, 2000); // Limit content length
        
        console.log(`✅ Website content fetched: ${websiteContent.length} characters`);
        console.log(`📄 Content preview: ${websiteContent.substring(0, 200)}...`);
      }
    } catch (fetchError) {
      console.log('❌ Could not fetch website content directly:', fetchError.message);
    }

    // Call the backend AI with enhanced prompt and real website content
    const aiQuery = `WEBSITE ANALYSIS TASK: Analyze the company website at ${url}

${websiteContent ? `WEBSITE CONTENT:\n${websiteContent}\n\n` : ''}Please analyze the above website content and extract the following information:

REQUIRED COMPANY DATA:
- Company Name: [exact company name from website]
- Industry: [specific industry/sector]
- Business Stage: [startup/growth/mature/enterprise]
- Mission Statement: [exact mission statement from website, in quotes]

STRATEGIC OBJECTIVES (SMART FORMAT):
Generate exactly 3 strategic objectives that follow SMART criteria (Specific, Measurable, Actionable, Realistic, Time-bound):

Example format:
1. [Specific Action] by [Timeframe] to achieve [Measurable Outcome]
2. [Specific Action] by [Timeframe] to achieve [Measurable Outcome]  
3. [Specific Action] by [Timeframe] to achieve [Measurable Outcome]

CRITICAL REQUIREMENTS: 
- Use ONLY the provided website content - do not make up information
- Find the exact mission statement from the website content (look for "mission", "about", "what we do")
- If no explicit mission found, extract the main value proposition from homepage
- Strategic objectives must be industry-specific and actionable (like "Integrate with Plaid API", "Support Stripe payments", "Target $10-100M revenue companies")
- Each objective must include specific technologies, metrics, or business strategies mentioned on the website
- Avoid generic objectives like "increase traffic" - focus on the company's specific business model and offerings

EXAMPLES OF GOOD OBJECTIVES:
- "Integrate payment processing with 5 major providers (Stripe, PayPal, Square) by Q2 2024"
- "Reduce customer onboarding time from 2 weeks to 3 days using automated workflows"  
- "Launch freemium tier capped at $100K annual revenue to capture SMB market"
- "Build API integrations with top 10 CRM systems (Salesforce, HubSpot, etc) by year-end"

FORMAT RESPONSE AS:
Company Name: [exact name from website content]
Industry: [specific industry based on website offerings]
Business Stage: [startup/growth/mature based on website language and team size]
Mission Statement: "[exact quote from website or main value proposition]"

Strategic Objectives:
1. [Specific, industry-relevant objective with metrics and timeline]
2. [Specific, industry-relevant objective with metrics and timeline]
3. [Specific, industry-relevant objective with metrics and timeline]`;

    console.log('🤖 Sending request to AI backend...');
    
    const response = await fetch('http://localhost:8002/api/ai-teams/strategic-intelligence', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: aiQuery,
        frameworks: ["ICE"]
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend API returned ${response.status}`);
    }

    const result = await response.json();
    
    console.log('\n📊 AI ANALYSIS RESULTS:');
    console.log('=' .repeat(50));
    console.log(result.analysis?.strategic_recommendation || 'No analysis available');
    console.log('=' .repeat(50));
    
    const analysis = result.analysis?.strategic_recommendation || '';
    
    // Extract structured data
    const name = analysis.match(/Company Name:\s*([^\n\r]+)/i)?.[1]?.trim();
    const industry = analysis.match(/Industry:\s*([^\n\r]+)/i)?.[1]?.trim();
    const stage = analysis.match(/Business Stage:\s*([^\n\r]+)/i)?.[1]?.trim();
    const mission = analysis.match(/Mission Statement:\s*"([^"]+)"/i)?.[1]?.trim() ||
                    analysis.match(/Mission Statement:\s*([^\n]+)/i)?.[1]?.trim();

    // Extract strategic objectives
    const objectives = [];
    const objectivesSection = analysis.match(/Strategic Objectives:\s*\n([\s\S]*?)(?:\n\n|$)/i);
    if (objectivesSection) {
      const objectivesText = objectivesSection[1];
      const objectiveMatches = objectivesText.match(/\d+\.\s+(.+)/g);
      
      if (objectiveMatches) {
        for (const match of objectiveMatches) {
          const objective = match.replace(/^\d+\.\s+/, '').trim();
          if (objective.length > 20 && objectives.length < 3) {
            objectives.push(objective);
          }
        }
      }
    }

    console.log('\n📈 EXTRACTED DATA:');
    console.log(`Company Name: ${name || 'Not found'}`);
    console.log(`Industry: ${industry || 'Not found'}`);
    console.log(`Business Stage: ${stage || 'Not found'}`);
    console.log(`Mission Statement: ${mission || 'Not found'}`);
    console.log(`Strategic Objectives: ${objectives.length} found`);
    
    objectives.forEach((obj, index) => {
      console.log(`${index + 1}. ${obj}`);
    });

    console.log(`\n⚡ Processing time: ${result.processing_time_ms}ms`);
    console.log(`🤖 AI Engine: ${result.analysis?.ai_engine_used || 'unknown'}`);
    console.log(`🎯 Confidence: ${result.confidence_score || 'unknown'}`);
    
    return {
      success: true,
      companyInfo: { name, industry, stage, mission },
      objectives,
      processingTime: result.processing_time_ms
    };

  } catch (error) {
    console.error(`❌ Error testing ${url}:`, error.message);
    return { success: false, error: error.message };
  }
}

async function runTests() {
  console.log('🚀 Starting Website Analysis Tests');
  console.log('Testing enhanced AI prompting with real website content');
  
  const testUrls = [
    'https://b33.tech',
    'https://google.com'
  ];
  
  for (const url of testUrls) {
    const result = await testWebsiteAnalysis(url);
    
    if (result.success) {
      console.log(`✅ ${url} test passed`);
    } else {
      console.log(`❌ ${url} test failed: ${result.error}`);
    }
    
    console.log('\n' + '-'.repeat(80) + '\n');
  }
}

runTests().catch(console.error);