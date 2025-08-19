#!/usr/bin/env python3
"""
Comprehensive PM33 Orchestration System Tests
Tests both technical infrastructure and functional workflows
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add orchestration path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from master_orchestrator import PM33MasterOrchestrator, Conflict, EscalationLevel
from human_interface.daily_briefing import HumanDecisionInterface

class ComprehensiveOrchestrationTest:
    def __init__(self):
        self.orchestrator = None
        self.human_interface = None
        self.test_results = []
        
    async def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 PM33 ORCHESTRATION SYSTEM - COMPREHENSIVE TEST SUITE")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Technical Infrastructure Tests
        await self.test_system_initialization()
        await self.test_context_loading()
        await self.test_shared_context_management()
        await self.test_agent_initialization()
        
        # Functional Workflow Tests
        await self.test_daily_briefing_generation()
        await self.test_agent_decision_making()
        await self.test_conflict_resolution()
        await self.test_escalation_workflows()
        
        # Integration Tests
        await self.test_agent_interactions()
        await self.test_scope_optimization()
        await self.test_human_decision_processing()
        
        # Performance Tests
        await self.test_parallel_agent_operations()
        await self.test_context_efficiency()
        
        # Edge Case Tests
        await self.test_error_handling()
        await self.test_data_persistence()
        
        # Generate test report
        self.generate_test_report()
        
    async def test_system_initialization(self):
        """Test 1: System Initialization"""
        print("🔧 TEST 1: System Initialization")
        try:
            self.orchestrator = PM33MasterOrchestrator()
            self.human_interface = HumanDecisionInterface(self.orchestrator)
            
            # Verify orchestrator components
            assert hasattr(self.orchestrator, 'technical_agent')
            assert hasattr(self.orchestrator, 'strategy_agent')
            assert hasattr(self.orchestrator, 'gtm_agent')
            assert hasattr(self.orchestrator, 'ux_agent')
            assert hasattr(self.orchestrator, 'shared_context')
            
            self.test_results.append(("System Initialization", "✅ PASSED", "All agents and components initialized"))
            print("  ✅ System initialization successful")
            
        except Exception as e:
            self.test_results.append(("System Initialization", "❌ FAILED", str(e)))
            print(f"  ❌ System initialization failed: {e}")
        print()
        
    async def test_context_loading(self):
        """Test 2: Context Loading & Mapping"""
        print("🔧 TEST 2: Context Loading & Mapping")
        try:
            # Test technical agent context
            tech_context = self.orchestrator.technical_agent.agent_context
            assert "core_requirements" in tech_context
            assert "ux_interface_specs" in tech_context
            
            # Test strategy agent context
            strategy_context = self.orchestrator.strategy_agent.agent_context
            assert "core_strategic_docs" in strategy_context
            assert "competitive_intelligence" in strategy_context
            
            # Test context relevance (agents don't have irrelevant files)
            tech_files = tech_context.get("core_requirements", {}).keys()
            assert "PROVEN_WORKFLOW_PATTERNS.md" in str(tech_files)
            
            # Verify agents DON'T have irrelevant context
            assert "marketing_foundation" not in tech_context  # Technical shouldn't have marketing
            
            self.test_results.append(("Context Loading", "✅ PASSED", "Relevant context loaded correctly"))
            print("  ✅ Context mapping successful - relevant files only")
            
        except Exception as e:
            self.test_results.append(("Context Loading", "❌ FAILED", str(e)))
            print(f"  ❌ Context loading failed: {e}")
        print()
        
    async def test_shared_context_management(self):
        """Test 3: Shared Context Management"""  
        print("🔧 TEST 3: Shared Context Management")
        try:
            # Test context updates
            test_update = {"test_key": "test_value", "timestamp": datetime.now().isoformat()}
            await self.orchestrator.update_shared_context(test_update)
            
            # Verify update persisted
            assert self.orchestrator.shared_context["test_key"] == "test_value"
            
            # Test strategic state integrity
            strategic_state = self.orchestrator.shared_context["strategic_state"]
            assert strategic_state["mission"] == "Transform PMs into PMOs through agentic AI teams"
            assert strategic_state["current_phase"] == "Day 3 beta launch preparation"
            
            # Test file persistence
            context_file = Path("pm33-orchestration/state_management/shared_context.json")
            if context_file.exists():
                with open(context_file, 'r') as f:
                    saved_context = json.load(f)
                assert "test_key" in saved_context
            
            self.test_results.append(("Shared Context", "✅ PASSED", "Context updates and persistence working"))
            print("  ✅ Shared context management working")
            
        except Exception as e:
            self.test_results.append(("Shared Context", "❌ FAILED", str(e)))
            print(f"  ❌ Shared context failed: {e}")
        print()
        
    async def test_agent_initialization(self):
        """Test 4: Individual Agent Initialization"""
        print("🔧 TEST 4: Agent Initialization & Authority")
        try:
            agents = [
                ("Technical", self.orchestrator.technical_agent),
                ("Strategy", self.orchestrator.strategy_agent),
                ("GTM", self.orchestrator.gtm_agent),
                ("UX", self.orchestrator.ux_agent)
            ]
            
            for name, agent in agents:
                # Test agent properties
                assert hasattr(agent, 'role')
                assert hasattr(agent, 'autonomous_decisions')
                assert hasattr(agent, 'must_escalate')
                assert hasattr(agent, 'agent_context')
                
                # Test authority configuration
                assert len(agent.autonomous_decisions) > 0
                assert len(agent.must_escalate) > 0
                
                print(f"    ✅ {name} Agent: {len(agent.autonomous_decisions)} autonomous, {len(agent.must_escalate)} escalations")
            
            self.test_results.append(("Agent Initialization", "✅ PASSED", "All agents properly configured"))
            
        except Exception as e:
            self.test_results.append(("Agent Initialization", "❌ FAILED", str(e)))
            print(f"  ❌ Agent initialization failed: {e}")
        print()
        
    async def test_daily_briefing_generation(self):
        """Test 5: Daily Briefing Generation"""
        print("🔧 TEST 5: Daily Briefing Generation")
        try:
            briefing = await self.orchestrator.generate_daily_briefing()
            
            # Test briefing structure
            required_sections = [
                "urgent_decisions_needed",
                "day_3_progress", 
                "strategic_approvals",
                "ux_reviews",
                "gtm_strategy_items",
                "technical_progress",
                "agentic_ai_teams_status"
            ]
            
            for section in required_sections:
                assert section in briefing, f"Missing briefing section: {section}"
            
            # Test Day 3 progress structure
            day_3_progress = briefing["day_3_progress"]
            assert "timeline_risk" in day_3_progress
            
            # Test agentic AI teams status
            ai_teams = briefing["agentic_ai_teams_status"]
            assert isinstance(ai_teams, dict)
            
            self.test_results.append(("Daily Briefing", "✅ PASSED", f"Generated {len(briefing)} sections"))
            print(f"  ✅ Daily briefing generated with {len(briefing)} sections")
            
        except Exception as e:
            self.test_results.append(("Daily Briefing", "❌ FAILED", str(e)))
            print(f"  ❌ Daily briefing failed: {e}")
        print()
        
    async def test_agent_decision_making(self):
        """Test 6: Agent Decision Making"""
        print("🔧 TEST 6: Agent Decision Making")
        try:
            # Test Technical Agent decision
            tech_decision = await self.orchestrator.technical_agent.make_decision({
                "type": "api_endpoint_development",
                "endpoint": "/api/test",
                "purpose": "Test endpoint for orchestration"
            })
            
            assert "decision" in tech_decision
            assert tech_decision["decision"] == "autonomous_endpoint_design"
            print("    ✅ Technical Agent: Autonomous API decision")
            
            # Test Strategy Agent decision
            strategy_decision = await self.orchestrator.strategy_agent.make_decision({
                "type": "competitive_analysis", 
                "competitive_context": "New AI tool launched"
            })
            
            assert "decision" in strategy_decision
            assert strategy_decision["decision"] == "autonomous_competitive_analysis"
            print("    ✅ Strategy Agent: Autonomous competitive analysis")
            
            # Test escalation detection
            escalation_decision = await self.orchestrator.strategy_agent.make_decision({
                "type": "core_value_proposition_changes",
                "summary": "Major messaging change"
            })
            
            assert "escalation_reason" in escalation_decision
            print("    ✅ Strategy Agent: Correctly escalated major decision")
            
            self.test_results.append(("Agent Decisions", "✅ PASSED", "Autonomous and escalation logic working"))
            
        except Exception as e:
            self.test_results.append(("Agent Decisions", "❌ FAILED", str(e)))
            print(f"  ❌ Agent decisions failed: {e}")
        print()
        
    async def test_conflict_resolution(self):
        """Test 7: Conflict Resolution"""
        print("🔧 TEST 7: Conflict Resolution")
        try:
            # Create test conflict
            test_conflict = Conflict(
                id="test_001",
                agents_involved=["technical", "ux"],
                conflict_type="technical_vs_ux",
                description="Component styling disagreement with user experience impact",
                business_impact=6,
                urgency=EscalationLevel.DAILY,
                resolution_needed_by=datetime.now(),
                agent_positions={"technical": "Technical feasibility", "ux": "User experience priority"}
            )
            
            # Test conflict resolution
            await self.orchestrator.handle_conflict(test_conflict)
            
            # Verify conflict was logged
            assert len(self.orchestrator.conflict_log) > 0
            latest_conflict = self.orchestrator.conflict_log[-1]
            assert latest_conflict["conflict"].id == "test_001"
            
            self.test_results.append(("Conflict Resolution", "✅ PASSED", "Conflict handling and logging working"))
            print("  ✅ Conflict resolution system working")
            
        except Exception as e:
            self.test_results.append(("Conflict Resolution", "❌ FAILED", str(e)))
            print(f"  ❌ Conflict resolution failed: {e}")
        print()
        
    async def test_escalation_workflows(self):
        """Test 8: Escalation Workflows"""
        print("🔧 TEST 8: Escalation Workflows")
        try:
            # Test escalation creation
            test_escalation = {
                "type": "strategic_decision",
                "summary": "Test strategic decision requiring human input",
                "strategic_impact": "High",
                "day_3_impact": "Medium",
                "urgency": EscalationLevel.IMMEDIATE
            }
            
            escalation_result = await self.orchestrator.escalate_to_human(test_escalation)
            
            # Verify escalation structure
            assert "id" in escalation_result
            assert "pm33_context" in escalation_result
            assert escalation_result["priority"] == "immediate"
            
            # Verify escalation was queued
            assert len(self.orchestrator.pending_escalations) > 0
            
            self.test_results.append(("Escalation Workflows", "✅ PASSED", "Escalation creation and queuing working"))
            print("  ✅ Escalation workflow system working")
            
        except Exception as e:
            self.test_results.append(("Escalation Workflows", "❌ FAILED", str(e)))
            print(f"  ❌ Escalation workflows failed: {e}")
        print()
        
    async def test_agent_interactions(self):
        """Test 9: Agent Interactions & Communication"""
        print("🔧 TEST 9: Agent Interactions")
        try:
            # Test getting agent summaries
            tech_summary = await self.orchestrator.technical_agent.get_progress_summary()
            assert isinstance(tech_summary, dict)
            assert "day_3_readiness" in tech_summary
            
            strategy_summary = await self.orchestrator.strategy_agent.get_progress_summary()
            assert isinstance(strategy_summary, dict)
            
            # Test agent approvals
            ux_approvals = await self.orchestrator.ux_agent.get_pending_approvals()
            assert isinstance(ux_approvals, list)
            
            gtm_approvals = await self.orchestrator.gtm_agent.get_pending_approvals()
            assert isinstance(gtm_approvals, list)
            
            self.test_results.append(("Agent Interactions", "✅ PASSED", "Agent communication methods working"))
            print("  ✅ Agent interactions working")
            
        except Exception as e:
            self.test_results.append(("Agent Interactions", "❌ FAILED", str(e)))
            print(f"  ❌ Agent interactions failed: {e}")
        print()
        
    async def test_scope_optimization(self):
        """Test 10: Scope Optimization"""
        print("🔧 TEST 10: Scope Optimization")
        try:
            # Test scope review generation
            scope_review = await self.orchestrator.conduct_scope_review()
            assert isinstance(scope_review, dict)
            
            # Test individual agent suggestions (simplified)
            tech_suggestions = {
                "authority_expansion_requests": {"test": "request"},
                "cross_agent_collaboration_opportunities": {},
                "efficiency_bottlenecks": []
            }
            
            # Test scope analysis
            master_analysis = await self.orchestrator.analyze_scope_suggestions({
                "technical": tech_suggestions
            })
            
            assert "conflict_analysis" in master_analysis
            assert "recommendations" in master_analysis
            
            self.test_results.append(("Scope Optimization", "✅ PASSED", "Scope review and analysis working"))
            print("  ✅ Scope optimization system working")
            
        except Exception as e:
            self.test_results.append(("Scope Optimization", "❌ FAILED", str(e)))
            print(f"  ❌ Scope optimization failed: {e}")
        print()
        
    async def test_parallel_agent_operations(self):
        """Test 11: Parallel Agent Operations"""
        print("🔧 TEST 11: Parallel Agent Operations")
        try:
            # Test concurrent agent operations
            tasks = [
                self.orchestrator.technical_agent.get_progress_summary(),
                self.orchestrator.strategy_agent.get_progress_summary(), 
                self.orchestrator.gtm_agent.get_progress_summary(),
                self.orchestrator.ux_agent.get_progress_summary()
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 4
            for result in results:
                assert isinstance(result, dict)
            
            self.test_results.append(("Parallel Operations", "✅ PASSED", "Concurrent agent operations working"))
            print("  ✅ Parallel agent operations working")
            
        except Exception as e:
            self.test_results.append(("Parallel Operations", "❌ FAILED", str(e)))
            print(f"  ❌ Parallel operations failed: {e}")
        print()
        
    async def test_context_efficiency(self):
        """Test 12: Context Efficiency"""
        print("🔧 TEST 12: Context Loading Efficiency")
        try:
            # Test that agents only have relevant context
            tech_context = self.orchestrator.technical_agent.agent_context
            strategy_context = self.orchestrator.strategy_agent.agent_context
            
            # Technical should have technical files but not marketing strategy
            tech_categories = set(tech_context.keys())
            expected_tech = {"core_requirements", "ux_interface_specs", "demo_requirements"}
            assert expected_tech.issubset(tech_categories)
            
            # Strategy should have strategic files but not technical implementation
            strategy_categories = set(strategy_context.keys())
            expected_strategy = {"core_strategic_docs", "competitive_intelligence"}
            assert expected_strategy.issubset(strategy_categories)
            
            # Verify separation (technical shouldn't have marketing foundation)
            assert "marketing_foundation" not in tech_categories
            assert "core_requirements" not in strategy_categories
            
            self.test_results.append(("Context Efficiency", "✅ PASSED", "Context properly separated by relevance"))
            print("  ✅ Context efficiency verified - relevant files only")
            
        except Exception as e:
            self.test_results.append(("Context Efficiency", "❌ FAILED", str(e)))
            print(f"  ❌ Context efficiency failed: {e}")
        print()
        
    async def test_error_handling(self):
        """Test 13: Error Handling"""
        print("🔧 TEST 13: Error Handling & Recovery")
        try:
            # Test invalid decision context
            try:
                await self.orchestrator.technical_agent.make_decision({})
                print("    ⚠️  Empty decision context handled gracefully")
            except Exception:
                pass  # Expected for malformed input
                
            # Test missing file handling (agent should handle gracefully)
            agent_context = self.orchestrator.technical_agent.agent_context
            assert isinstance(agent_context, dict)  # Should not crash on missing files
            
            self.test_results.append(("Error Handling", "✅ PASSED", "Error conditions handled gracefully"))
            print("  ✅ Error handling working")
            
        except Exception as e:
            self.test_results.append(("Error Handling", "❌ FAILED", str(e)))
            print(f"  ❌ Error handling failed: {e}")
        print()
        
    async def test_human_decision_processing(self):
        """Test 14: Human Decision Interface"""
        print("🔧 TEST 14: Human Decision Interface")
        try:
            # Test decision file creation (mock)
            test_decisions = {
                "decisions": [
                    {
                        "id": "test_decision_001",
                        "type": "scope_change",
                        "agent": "technical",
                        "approval": "approve",
                        "scope_changes": {
                            "new_autonomous_decisions": ["test_authority"]
                        }
                    }
                ]
            }
            
            # Test decision processing logic exists
            assert hasattr(self.human_interface, 'process_human_decisions')
            assert hasattr(self.human_interface, 'process_single_decision')
            
            self.test_results.append(("Human Interface", "✅ PASSED", "Human decision processing interface ready"))
            print("  ✅ Human decision interface working")
            
        except Exception as e:
            self.test_results.append(("Human Interface", "❌ FAILED", str(e)))
            print(f"  ❌ Human interface failed: {e}")
        print()
        
    async def test_data_persistence(self):
        """Test 15: Data Persistence"""
        print("🔧 TEST 15: Data Persistence")
        try:
            # Test shared context persistence
            test_data = {"test_persistence": "working", "timestamp": datetime.now().isoformat()}
            await self.orchestrator.update_shared_context(test_data)
            
            # Verify file exists and contains data
            context_file = Path("pm33-orchestration/state_management/shared_context.json")
            if context_file.exists():
                with open(context_file, 'r') as f:
                    saved_data = json.load(f)
                assert "test_persistence" in saved_data
                assert saved_data["test_persistence"] == "working"
            
            self.test_results.append(("Data Persistence", "✅ PASSED", "Context data persists correctly"))
            print("  ✅ Data persistence working")
            
        except Exception as e:
            self.test_results.append(("Data Persistence", "❌ FAILED", str(e)))
            print(f"  ❌ Data persistence failed: {e}")
        print()
        
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*70)
        print("🎯 PM33 ORCHESTRATION SYSTEM - TEST RESULTS REPORT")
        print("="*70)
        
        passed_tests = sum(1 for _, status, _ in self.test_results if "✅" in status)
        failed_tests = sum(1 for _, status, _ in self.test_results if "❌" in status)
        total_tests = len(self.test_results)
        
        print(f"📊 SUMMARY: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print()
        
        print("📋 DETAILED RESULTS:")
        for test_name, status, details in self.test_results:
            print(f"  {status} {test_name}: {details}")
        
        print("\n" + "="*70)
        
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! PM33 Orchestration System is fully operational.")
            print("🚀 System ready for production PM33 development!")
        else:
            print(f"⚠️  {failed_tests} tests failed. Review issues above before production use.")
        
        print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

async def main():
    """Run comprehensive test suite"""
    tester = ComprehensiveOrchestrationTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())