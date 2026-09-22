import asyncio
import logging
from app.database import get_supabase
from app.services.resource_monitor import ResourceMonitor

logger = logging.getLogger(__name__)

async def run_cron_monitor():
    while True:
        try:
            logger.info("Running backend cron monitor...")
            supabase = get_supabase()
            
            # 1. Get all tasks with auto_monitor_enabled = True
            tasks_resp = supabase.table('tasks').select('id, user_id').eq('auto_monitor_enabled', True).execute()
            
            if tasks_resp.data:
                task_ids = [t['id'] for t in tasks_resp.data]
                
                # 2. Get resources that are active and not ignored
                res_resp = supabase.table('task_resources').select('*').in_('task_id', task_ids).is_('replaced_by_resource_id', 'null').execute()
                resources = [r for r in res_resp.data if not r.get('is_ignored')]
                
                if resources:
                    monitor = ResourceMonitor(supabase)
                    
                    async def check_single(r):
                        try:
                            await monitor.check_resource(r['id'], r['url'], r.get('content_hash'), r['user_id'], r['task_id'])
                        except Exception as e:
                            logger.error(f"Error checking resource {r['id']}: {e}")
                    
                    # 3. Check all concurrently
                    await asyncio.gather(*[check_single(r) for r in resources])
                    logger.info(f"Cron check completed for {len(resources)} resources.")
                else:
                    logger.info("No active resources found to monitor.")
            else:
                logger.info("No tasks have auto-monitor enabled.")
                
        except Exception as e:
            logger.error(f"Backend cron monitor error: {e}")
            
        # Wait 30 seconds before next run
        await asyncio.sleep(30)
