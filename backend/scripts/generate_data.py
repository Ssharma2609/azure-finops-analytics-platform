#!/usr/bin/env python3
"""
Synthetic data generation script for Azure Cost Intelligence Simulator.

Generates realistic Azure-like cost data including:
- Subscriptions with different environments
- Resource groups across regions
- Various Azure services
- Daily cost and usage records with trends and spikes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import uuid
from datetime import date, timedelta, datetime
from typing import List, Dict, Any
import numpy as np
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models import Subscription, ResourceGroup, Service, Resource, CostUsage


# Configuration
NUM_SUBSCRIPTIONS = 5
RESOURCE_GROUPS_PER_SUB = [3, 5]  # min, max
RESOURCES_PER_RG = [5, 15]  # min, max
HISTORY_DAYS = 90

# Azure regions
REGIONS = [
    "eastus", "eastus2", "westus", "westus2", "centralus",
    "northeurope", "westeurope", "uksouth", "ukwest",
    "southeastasia", "eastasia", "australiaeast",
]

# Environments
ENVIRONMENTS = ["production", "development", "test", "staging"]
ENV_WEIGHTS = [0.4, 0.3, 0.2, 0.1]

# Azure services with realistic characteristics
AZURE_SERVICES = [
    {
        "name": "Virtual Machines",
        "category": "Compute",
        "base_cost": 50.0,
        "cost_variance": 200.0,
        "types": ["Standard_D2_v3", "Standard_D4_v3", "Standard_D8_v3", "Standard_B2ms", "Standard_E4_v3"],
        "unit": "hours",
    },
    {
        "name": "App Service",
        "category": "Compute",
        "base_cost": 30.0,
        "cost_variance": 100.0,
        "types": ["Basic", "Standard", "Premium", "PremiumV2"],
        "unit": "hours",
    },
    {
        "name": "Azure SQL Database",
        "category": "Database",
        "base_cost": 100.0,
        "cost_variance": 500.0,
        "types": ["Basic", "Standard", "Premium", "BusinessCritical"],
        "unit": "DTUs",
    },
    {
        "name": "Cosmos DB",
        "category": "Database",
        "base_cost": 50.0,
        "cost_variance": 300.0,
        "types": ["Provisioned", "Serverless"],
        "unit": "RUs",
    },
    {
        "name": "Storage Account",
        "category": "Storage",
        "base_cost": 5.0,
        "cost_variance": 50.0,
        "types": ["StorageV2", "BlobStorage", "FileStorage"],
        "unit": "GB",
    },
    {
        "name": "Azure Functions",
        "category": "Compute",
        "base_cost": 5.0,
        "cost_variance": 30.0,
        "types": ["Consumption", "Premium"],
        "unit": "executions",
    },
    {
        "name": "Azure Kubernetes Service",
        "category": "Compute",
        "base_cost": 150.0,
        "cost_variance": 500.0,
        "types": ["Standard", "Basic"],
        "unit": "nodes",
    },
    {
        "name": "Azure CDN",
        "category": "Networking",
        "base_cost": 10.0,
        "cost_variance": 100.0,
        "types": ["Standard", "Premium"],
        "unit": "GB transferred",
    },
    {
        "name": "Application Gateway",
        "category": "Networking",
        "base_cost": 80.0,
        "cost_variance": 150.0,
        "types": ["Standard_v2", "WAF_v2"],
        "unit": "hours",
    },
    {
        "name": "Azure Monitor",
        "category": "Management",
        "base_cost": 10.0,
        "cost_variance": 50.0,
        "types": ["Basic", "Standard"],
        "unit": "GB ingested",
    },
    {
        "name": "Key Vault",
        "category": "Security",
        "base_cost": 2.0,
        "cost_variance": 10.0,
        "types": ["Standard", "Premium"],
        "unit": "operations",
    },
    {
        "name": "Redis Cache",
        "category": "Database",
        "base_cost": 40.0,
        "cost_variance": 200.0,
        "types": ["Basic", "Standard", "Premium"],
        "unit": "hours",
    },
]

# Team names for tags
TEAMS = ["platform", "data", "frontend", "backend", "devops", "security", "mobile"]
PROJECTS = ["alpha", "beta", "gamma", "delta", "epsilon", "omega"]


def generate_subscription_name(env: str) -> str:
    """Generate realistic subscription name."""
    prefixes = ["Corp", "Enterprise", "Cloud", "Digital", "Tech"]
    return f"{random.choice(prefixes)}-{env.capitalize()}-{random.randint(1, 99):02d}"


def generate_resource_group_name(sub_name: str) -> str:
    """Generate realistic resource group name."""
    purposes = ["web", "api", "data", "infra", "shared", "app", "platform"]
    return f"rg-{random.choice(purposes)}-{random.choice(REGIONS)[:3]}-{random.randint(1, 9)}"


def generate_resource_name(service_name: str, rg_name: str) -> str:
    """Generate realistic resource name."""
    service_prefix = {
        "Virtual Machines": "vm",
        "App Service": "app",
        "Azure SQL Database": "sql",
        "Cosmos DB": "cosmos",
        "Storage Account": "st",
        "Azure Functions": "func",
        "Azure Kubernetes Service": "aks",
        "Azure CDN": "cdn",
        "Application Gateway": "agw",
        "Azure Monitor": "mon",
        "Key Vault": "kv",
        "Redis Cache": "redis",
    }
    prefix = service_prefix.get(service_name, "res")
    suffix = uuid.uuid4().hex[:6]
    return f"{prefix}-{suffix}"


def generate_daily_cost(
    base_cost: float,
    day_index: int,
    total_days: int,
    env: str,
    add_spike: bool = False,
    add_trend: bool = False,
) -> float:
    """
    Generate realistic daily cost with patterns.
    
    Includes:
    - Day of week patterns (lower on weekends for dev/test)
    - Random noise
    - Optional trend (increasing/decreasing over time)
    - Optional spikes for anomaly detection
    """
    cost = base_cost
    
    # Apply environment factor
    env_factors = {
        "production": 1.0,
        "staging": 0.5,
        "development": 0.3,
        "test": 0.2,
    }
    cost *= env_factors.get(env, 0.5)
    
    # Add random noise (±20%)
    noise = random.uniform(0.8, 1.2)
    cost *= noise
    
    # Day of week pattern (lower on weekends for non-prod)
    day_of_week = (day_index % 7)
    if env != "production" and day_of_week in [5, 6]:
        cost *= random.uniform(0.3, 0.6)
    
    # Add trend if specified
    if add_trend:
        trend_factor = 1 + (day_index / total_days) * 0.3  # Up to 30% increase
        cost *= trend_factor
    
    # Add spike if specified
    if add_spike:
        if random.random() < 0.03:  # 3% chance of spike
            spike_factor = random.uniform(2.0, 4.0)
            cost *= spike_factor
    
    return max(0.01, cost)


def create_services(db: Session) -> Dict[str, Service]:
    """Create service records."""
    services = {}
    
    for svc_data in AZURE_SERVICES:
        service = Service(
            name=svc_data["name"],
            category=svc_data["category"],
            description=f"Azure {svc_data['name']} service",
            base_unit_cost=svc_data["base_cost"],
            unit_type=svc_data["unit"],
        )
        db.add(service)
        services[svc_data["name"]] = service
    
    db.commit()
    return services


def create_subscriptions(db: Session) -> List[Subscription]:
    """Create subscription records."""
    subscriptions = []
    
    for i in range(NUM_SUBSCRIPTIONS):
        env = random.choices(ENVIRONMENTS, weights=ENV_WEIGHTS)[0]
        
        # Budget varies by environment
        budget_map = {
            "production": random.randint(5000, 20000),
            "staging": random.randint(1000, 5000),
            "development": random.randint(500, 2000),
            "test": random.randint(200, 1000),
        }
        
        subscription = Subscription(
            subscription_id=f"sub-{uuid.uuid4().hex[:12]}",
            name=generate_subscription_name(env),
            state="Active",
            environment=env,
            owner_email=f"owner-{i+1}@contoso.com",
            budget_limit=str(budget_map[env]),
            is_active=True,
        )
        db.add(subscription)
        subscriptions.append(subscription)
    
    db.commit()
    return subscriptions


def create_resource_groups(
    db: Session,
    subscriptions: List[Subscription],
) -> List[ResourceGroup]:
    """Create resource group records."""
    resource_groups = []
    
    for sub in subscriptions:
        num_rgs = random.randint(*RESOURCE_GROUPS_PER_SUB)
        
        for _ in range(num_rgs):
            rg = ResourceGroup(
                name=generate_resource_group_name(sub.name),
                region=random.choice(REGIONS),
                subscription_id=sub.id,
                tags={
                    "env": sub.environment,
                    "team": random.choice(TEAMS),
                    "project": random.choice(PROJECTS),
                    "cost_center": f"CC-{random.randint(100, 999)}",
                },
            )
            db.add(rg)
            resource_groups.append(rg)
    
    db.commit()
    return resource_groups


def create_resources(
    db: Session,
    resource_groups: List[ResourceGroup],
    services: Dict[str, Service],
) -> List[Resource]:
    """Create resource records."""
    resources = []
    
    for rg in resource_groups:
        num_resources = random.randint(*RESOURCES_PER_RG)
        
        # Weight services based on environment
        service_list = list(AZURE_SERVICES)
        
        for _ in range(num_resources):
            svc_data = random.choice(service_list)
            service = services[svc_data["name"]]
            
            resource = Resource(
                resource_id=f"/subscriptions/{rg.subscription_id}/resourceGroups/{rg.name}/providers/{uuid.uuid4().hex[:8]}",
                name=generate_resource_name(svc_data["name"], rg.name),
                resource_type=svc_data["name"].replace(" ", ""),
                sku=random.choice(svc_data["types"]),
                region=rg.region,
                resource_group_id=rg.id,
                service_id=service.id,
                tags={
                    **rg.tags,
                    "created_by": "terraform",
                    "managed": random.choice(["true", "false"]),
                },
                properties={
                    "tier": random.choice(["Free", "Basic", "Standard", "Premium"]),
                    "size": random.choice(["Small", "Medium", "Large"]),
                },
                provisioning_state="Succeeded",
                is_active=random.random() > 0.1,  # 90% active
                last_activity_at=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
            )
            db.add(resource)
            resources.append((resource, svc_data))
    
    db.commit()
    return resources


def create_cost_records(
    db: Session,
    resources: List[tuple],
    subscriptions_map: Dict[uuid.UUID, Subscription],
) -> None:
    """Create daily cost and usage records."""
    today = date.today()
    start_date = today - timedelta(days=HISTORY_DAYS)
    
    batch_size = 1000
    batch = []
    
    for resource, svc_data in resources:
        # Get subscription environment
        rg = db.query(ResourceGroup).filter(ResourceGroup.id == resource.resource_group_id).first()
        sub = subscriptions_map.get(rg.subscription_id)
        env = sub.environment if sub else "development"
        
        # Determine resource patterns
        has_trend = random.random() < 0.3  # 30% of resources have trends
        has_spikes = random.random() < 0.2  # 20% of resources might have spikes
        
        base_cost = svc_data["base_cost"] + random.uniform(0, svc_data["cost_variance"])
        
        for day_offset in range(HISTORY_DAYS):
            current_date = start_date + timedelta(days=day_offset)
            
            # Skip some days for inactive resources
            if not resource.is_active and random.random() < 0.3:
                continue
            
            daily_cost = generate_daily_cost(
                base_cost=base_cost,
                day_index=day_offset,
                total_days=HISTORY_DAYS,
                env=env,
                add_spike=has_spikes,
                add_trend=has_trend,
            )
            
            usage_quantity = random.uniform(0.5, 24.0)
            
            # Idle resources have very low usage
            if resource.is_active and random.random() < 0.1:  # 10% are idle
                usage_quantity = random.uniform(0.0, 0.1)
            
            cost_record = CostUsage(
                resource_id=resource.id,
                usage_date=current_date,
                cost=daily_cost,
                pretax_cost=daily_cost * 0.85,
                usage_quantity=usage_quantity,
                unit_price=daily_cost / max(usage_quantity, 0.01),
                billing_currency="USD",
                meter_category=svc_data["category"],
                meter_subcategory=svc_data["name"],
                meter_name=f"{svc_data['name']} - {resource.sku}",
                consumed_quantity=usage_quantity,
                resource_rate=daily_cost / max(usage_quantity, 0.01),
            )
            batch.append(cost_record)
            
            if len(batch) >= batch_size:
                db.add_all(batch)
                db.commit()
                batch = []
    
    # Commit remaining records
    if batch:
        db.add_all(batch)
        db.commit()


def main():
    """Main data generation function."""
    print("=" * 60)
    print("Azure Cost Intelligence Simulator - Data Generator")
    print("=" * 60)
    
    # Create tables
    print("\n[1/7] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        print("[2/7] Clearing existing data...")
        db.query(CostUsage).delete()
        db.query(Resource).delete()
        db.query(ResourceGroup).delete()
        db.query(Service).delete()
        db.query(Subscription).delete()
        db.commit()
        
        # Create services
        print("[3/7] Creating Azure services...")
        services = create_services(db)
        print(f"       Created {len(services)} services")
        
        # Create subscriptions
        print("[4/7] Creating subscriptions...")
        subscriptions = create_subscriptions(db)
        subscriptions_map = {s.id: s for s in subscriptions}
        print(f"       Created {len(subscriptions)} subscriptions")
        
        # Create resource groups
        print("[5/7] Creating resource groups...")
        resource_groups = create_resource_groups(db, subscriptions)
        print(f"       Created {len(resource_groups)} resource groups")
        
        # Create resources
        print("[6/7] Creating resources...")
        resources = create_resources(db, resource_groups, services)
        print(f"       Created {len(resources)} resources")
        
        # Create cost records
        print(f"[7/7] Creating cost records ({HISTORY_DAYS} days of history)...")
        create_cost_records(db, resources, subscriptions_map)
        
        total_costs = db.query(CostUsage).count()
        print(f"       Created {total_costs} cost records")
        
        print("\n" + "=" * 60)
        print("Data generation complete!")
        print("=" * 60)
        
        # Print summary
        print("\nSummary:")
        print(f"  - Subscriptions: {len(subscriptions)}")
        print(f"  - Resource Groups: {len(resource_groups)}")
        print(f"  - Resources: {len(resources)}")
        print(f"  - Cost Records: {total_costs}")
        print(f"  - Date Range: {date.today() - timedelta(days=HISTORY_DAYS)} to {date.today()}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
