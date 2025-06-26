# Command: optimize-coordination

Optimize the coordination system performance and archive completed work: $ARGUMENTS

## Steps:

1. Analyze current system state:
   - Check work claims file sizes
   - Count active vs completed items
   - Calculate performance metrics

2. Run optimization:
   ```bash
   python coordination_cli_v2.py optimize
   ```

3. Additional optimizations based on arguments:
   - "aggressive" - Archive items older than 7 days
   - "cleanup" - Remove duplicate entries
   - "compact" - Minimize JSON formatting

4. Generate performance report:
   - Before/after file sizes
   - Items archived
   - Performance improvement estimate

5. Verify system integrity:
   - Check all active items are preserved
   - Validate JSON structure
   - Test fast-path functionality

## Examples:

- `/optimize-coordination` - Standard optimization
- `/optimize-coordination: aggressive` - Archive old items aggressively  
- `/optimize-coordination: cleanup compact` - Full cleanup and compaction

## Optimization Thresholds:

- Archive completed items > 24 hours old
- Compact files > 1000 lines
- Alert if active items > 100
- Backup before major changes

## Output Format:

```
🚀 Optimization Complete

📊 Results:
   Completed items archived: X
   File size reduction: Y%
   Performance improvement: ~Z ms
   
📁 Archive Details:
   Archive location: <path>
   Archive size: <size>
   Items archived: <count>
   
⚡ Performance Metrics:
   Before: <size> KB, <lines> lines
   After: <size> KB, <lines> lines
   Improvement: <percentage>%
   
✅ System Status: Healthy
   Active items: <count>
   Fast-path enabled: Yes
   Last optimization: <timestamp>
```