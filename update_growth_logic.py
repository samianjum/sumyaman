import re

path = 'apsokara/views.py'
with open(path, 'r') as f:
    content = f.read()

growth_logic = """
        # Subject-wise Growth Calculation
        for sub, data in subject_depth.items():
            if len(data['history']) >= 2:
                last_perf = data['history'][-1]['perc']
                prev_perf = data['history'][-2]['perc']
                data['change'] = round(last_perf - prev_perf, 1)
            else:
                data['change'] = 0
"""

if "data['change']" not in content:
    content = content.replace("'subject_depth': subject_depth", growth_logic + "\n        'subject_depth': subject_depth")
    with open(path, 'w') as f:
        f.write(content)
    print("✅ Growth logic added to views.py")
else:
    print("⚠️ Already exists.")
