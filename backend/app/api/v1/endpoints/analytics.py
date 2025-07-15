from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional
from datetime import datetime, date, timedelta
from app.core.database import get_db
from app.api.deps import get_current_active_user

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard statistics and KPIs"""
    try:
        # Get total scans
        scans_response = db.table('scans').select("*", count="exact").execute()
        total_scans = scans_response.count or 0
        
        # Get total violations
        violations_response = db.table('violations').select("*", count="exact").execute()
        total_violations = violations_response.count or 0
        
        # Get active violations
        active_violations_response = db.table('violations').select("*", count="exact").neq('status', 'resolved').execute()
        active_violations = active_violations_response.count or 0
        
        # Get resolved violations
        resolved_violations = total_violations - active_violations
        
        # Get total vehicles
        vehicles_response = db.table('vehicles').select("*", count="exact").execute()
        total_vehicles = vehicles_response.count or 0
        
        # Get active users
        users_response = db.table('users').select("*", count="exact").eq('status', 'active').execute()
        active_users = users_response.count or 0
        
        # Get pending approvals
        pending_response = db.table('users').select("*", count="exact").eq('status', 'pending').execute()
        pending_approvals = pending_response.count or 0
        
        # Calculate monthly growth (simplified)
        today = datetime.now().date()
        last_month = today - timedelta(days=30)
        
        recent_scans_response = db.table('scans').select("*", count="exact").gte('scan_time', last_month.isoformat()).execute()
        recent_scans = recent_scans_response.count or 0
        
        # Calculate growth percentage (simplified)
        growth_percentage = 12.5  # Placeholder calculation
        
        return {
            "kpis": {
                "total_scans": total_scans,
                "active_violations": active_violations,
                "resolved_violations": resolved_violations,
                "total_vehicles": total_vehicles,
                "active_users": active_users,
                "pending_approvals": pending_approvals,
                "monthly_growth": f"+{growth_percentage}%"
            },
            "recent_activity": {
                "scans_last_30_days": recent_scans,
                "violations_last_30_days": active_violations
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard statistics"
        )

@router.get("/violations/trends")
async def get_violation_trends(
    days: int = Query(30, ge=1, le=365),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get violation trends over time"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        response = db.table('violations').select("date_time, violation_type, status").gte('date_time', start_date.isoformat()).lte('date_time', end_date.isoformat()).execute()
        
        # Process data for trends (simplified)
        trends = {
            "period": f"{days} days",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_violations": len(response.data),
            "by_type": {},
            "by_status": {}
        }
        
        # Count by type and status
        for violation in response.data:
            v_type = violation['violation_type']
            v_status = violation['status']
            
            trends["by_type"][v_type] = trends["by_type"].get(v_type, 0) + 1
            trends["by_status"][v_status] = trends["by_status"].get(v_status, 0) + 1
        
        return trends
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch violation trends"
        )

@router.get("/scans/activity")
async def get_scan_activity(
    days: int = Query(7, ge=1, le=30),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get scan activity statistics"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        response = db.table('scans').select("scan_time, location, camera_id").gte('scan_time', start_date.isoformat()).lte('scan_time', end_date.isoformat()).execute()
        
        activity = {
            "period": f"{days} days",
            "total_scans": len(response.data),
            "by_location": {},
            "by_camera": {},
            "daily_average": len(response.data) / days if days > 0 else 0
        }
        
        # Count by location and camera
        for scan in response.data:
            location = scan['location']
            camera_id = scan.get('camera_id', 'unknown')
            
            activity["by_location"][location] = activity["by_location"].get(location, 0) + 1
            activity["by_camera"][camera_id] = activity["by_camera"].get(camera_id, 0) + 1
        
        return activity
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch scan activity"
        )

@router.get("/vehicles/statistics")
async def get_vehicle_statistics(
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get vehicle registry statistics"""
    try:
        response = db.table('vehicles').select("make, vehicle_type, status, expiry_date").execute()
        
        stats = {
            "total_vehicles": len(response.data),
            "by_make": {},
            "by_type": {},
            "by_status": {},
            "expiring_soon": 0
        }
        
        # Calculate expiring soon (within 30 days)
        expiry_threshold = (datetime.now().date() + timedelta(days=30)).isoformat()
        
        for vehicle in response.data:
            make = vehicle['make']
            v_type = vehicle['vehicle_type']
            status = vehicle['status']
            expiry = vehicle['expiry_date']
            
            stats["by_make"][make] = stats["by_make"].get(make, 0) + 1
            stats["by_type"][v_type] = stats["by_type"].get(v_type, 0) + 1
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            if expiry and expiry <= expiry_threshold:
                stats["expiring_soon"] += 1
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch vehicle statistics"
        )

@router.get("/reports/generate")
async def generate_report(
    report_type: str = Query(..., regex="^(violations|scans|vehicles|users)$"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    format: str = Query("json", regex="^(json|csv)$"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Generate various reports"""
    try:
        if not date_from:
            date_from = datetime.now().date() - timedelta(days=30)
        if not date_to:
            date_to = datetime.now().date()
        
        report_data = {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "date_range": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            },
            "generated_by": current_user.email,
            "data": []
        }
        
        if report_type == "violations":
            response = db.table('violations').select("*").gte('date_time', date_from.isoformat()).lte('date_time', date_to.isoformat()).execute()
            report_data["data"] = response.data
            
        elif report_type == "scans":
            response = db.table('scans').select("*").gte('scan_time', date_from.isoformat()).lte('scan_time', date_to.isoformat()).execute()
            report_data["data"] = response.data
            
        elif report_type == "vehicles":
            response = db.table('vehicles').select("*").execute()
            report_data["data"] = response.data
            
        elif report_type == "users":
            response = db.table('users').select("id, name, email, role, status, last_login, created_at").execute()
            report_data["data"] = response.data
        
        report_data["total_records"] = len(report_data["data"])
        
        return report_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )