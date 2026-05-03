"""
Cost optimization recommendation engine.
"""
from typing import List, Dict, Any
from datetime import datetime

from app.schemas.analytics import RecommendationType, RecommendationPriority


class CostRecommender:
    """
    Generates cost optimization recommendations based on usage patterns.
    
    Rules:
    - Idle resources (low usage, ongoing cost)
    - High-cost services (concentration risk)
    - Budget overruns
    - Reserved instance opportunities
    """
    
    def __init__(self):
        self.rules = [
            self._check_idle_resources,
            self._check_high_cost_services,
            self._check_budget_utilization,
            self._check_reserved_instance_opportunities,
            self._check_storage_optimization,
        ]
    
    def generate_recommendations(
        self,
        idle_resources: List[dict],
        service_costs: List[dict],
        subscription_costs: List[dict],
    ) -> List[dict]:
        """Generate all applicable recommendations."""
        recommendations = []
        
        context = {
            "idle_resources": idle_resources,
            "service_costs": service_costs,
            "subscription_costs": subscription_costs,
        }
        
        for rule in self.rules:
            recs = rule(context)
            recommendations.extend(recs)
        
        # Sort by estimated savings
        recommendations.sort(
            key=lambda x: x["estimated_monthly_savings"],
            reverse=True
        )
        
        return recommendations
    
    def _check_idle_resources(self, context: dict) -> List[dict]:
        """Generate recommendations for idle resources."""
        recommendations = []
        
        for resource in context["idle_resources"]:
            monthly_savings = resource["total_cost"]
            
            if monthly_savings < 10:
                continue
            
            if monthly_savings > 500:
                priority = RecommendationPriority.HIGH
            elif monthly_savings > 100:
                priority = RecommendationPriority.MEDIUM
            else:
                priority = RecommendationPriority.LOW
            
            recommendations.append({
                "type": RecommendationType.IDLE_RESOURCE,
                "priority": priority,
                "title": f"Idle resource detected: {resource['name']}",
                "description": (
                    f"Resource '{resource['name']}' ({resource['resource_type']}) "
                    f"shows minimal usage ({resource['avg_usage']:.2f}) but incurs "
                    f"${monthly_savings:.2f}/month. Consider shutting down or deleting."
                ),
                "estimated_monthly_savings": monthly_savings,
                "estimated_annual_savings": monthly_savings * 12,
                "confidence_score": 0.85,
                "resource_id": resource["resource_id"],
                "resource_name": resource["name"],
                "resource_type": resource["resource_type"],
                "service_name": resource["service_name"],
                "subscription_id": resource["subscription_id"],
                "action_required": "Review resource usage and delete if unused",
                "implementation_effort": "low",
            })
        
        return recommendations
    
    def _check_high_cost_services(self, context: dict) -> List[dict]:
        """Identify services with high cost concentration."""
        recommendations = []
        
        for service in context["service_costs"]:
            # Flag services that are >30% of total cost
            if service["percentage_of_total"] > 30:
                monthly_savings = service["total_cost"] * 0.1  # Assume 10% optimization potential
                
                recommendations.append({
                    "type": RecommendationType.RIGHTSIZING,
                    "priority": RecommendationPriority.MEDIUM,
                    "title": f"High cost concentration in {service['service_name']}",
                    "description": (
                        f"{service['service_name']} accounts for {service['percentage_of_total']:.1f}% "
                        f"of total costs (${service['total_cost']:.2f}). Review for rightsizing "
                        f"or reserved capacity opportunities."
                    ),
                    "estimated_monthly_savings": monthly_savings,
                    "estimated_annual_savings": monthly_savings * 12,
                    "confidence_score": 0.70,
                    "service_name": service["service_name"],
                    "action_required": "Review resource sizing and utilization",
                    "implementation_effort": "medium",
                })
        
        return recommendations
    
    def _check_budget_utilization(self, context: dict) -> List[dict]:
        """Check for budget overruns or approaching limits."""
        recommendations = []
        
        for sub in context["subscription_costs"]:
            if sub.get("budget_utilization") and sub["budget_utilization"] > 80:
                utilization = sub["budget_utilization"]
                
                if utilization >= 100:
                    priority = RecommendationPriority.HIGH
                    title = f"Budget exceeded for {sub['subscription_name']}"
                else:
                    priority = RecommendationPriority.MEDIUM
                    title = f"Budget warning for {sub['subscription_name']}"
                
                overage = max(0, sub["total_cost"] - (sub.get("budget_limit") or 0))
                
                recommendations.append({
                    "type": RecommendationType.RIGHTSIZING,
                    "priority": priority,
                    "title": title,
                    "description": (
                        f"Subscription '{sub['subscription_name']}' is at {utilization:.1f}% "
                        f"of budget. Current spend: ${sub['total_cost']:.2f}. "
                        f"Review and optimize resources."
                    ),
                    "estimated_monthly_savings": overage if overage > 0 else sub["total_cost"] * 0.1,
                    "estimated_annual_savings": (overage if overage > 0 else sub["total_cost"] * 0.1) * 12,
                    "confidence_score": 0.90,
                    "subscription_id": sub["subscription_id"],
                    "action_required": "Review subscription resources and implement cost controls",
                    "implementation_effort": "medium",
                })
        
        return recommendations
    
    def _check_reserved_instance_opportunities(self, context: dict) -> List[dict]:
        """Identify opportunities for reserved instances."""
        recommendations = []
        
        # Look for consistent high-cost compute services
        compute_services = [
            s for s in context["service_costs"]
            if s["service_category"] == "Compute" and s["total_cost"] > 1000
        ]
        
        for service in compute_services:
            # Reserved instances typically save 30-50%
            monthly_savings = service["total_cost"] * 0.35
            
            recommendations.append({
                "type": RecommendationType.RESERVED_INSTANCE,
                "priority": RecommendationPriority.MEDIUM,
                "title": f"Consider reserved instances for {service['service_name']}",
                "description": (
                    f"Your {service['service_name']} spend of ${service['total_cost']:.2f}/month "
                    f"could benefit from reserved instance pricing. Estimated savings: 30-50%."
                ),
                "estimated_monthly_savings": monthly_savings,
                "estimated_annual_savings": monthly_savings * 12,
                "confidence_score": 0.75,
                "service_name": service["service_name"],
                "action_required": "Evaluate 1-year or 3-year reserved instance commitments",
                "implementation_effort": "medium",
            })
        
        return recommendations
    
    def _check_storage_optimization(self, context: dict) -> List[dict]:
        """Check for storage optimization opportunities."""
        recommendations = []
        
        storage_services = [
            s for s in context["service_costs"]
            if s["service_category"] == "Storage" and s["total_cost"] > 500
        ]
        
        for service in storage_services:
            # Storage tiering typically saves 20-40%
            monthly_savings = service["total_cost"] * 0.25
            
            recommendations.append({
                "type": RecommendationType.STORAGE_OPTIMIZATION,
                "priority": RecommendationPriority.LOW,
                "title": f"Optimize storage tier for {service['service_name']}",
                "description": (
                    f"Review {service['service_name']} data for tiering opportunities. "
                    f"Moving infrequently accessed data to cooler tiers can save 20-40%."
                ),
                "estimated_monthly_savings": monthly_savings,
                "estimated_annual_savings": monthly_savings * 12,
                "confidence_score": 0.65,
                "service_name": service["service_name"],
                "action_required": "Implement lifecycle policies and data tiering",
                "implementation_effort": "low",
            })
        
        return recommendations
