path = 'templates/hq_admin_custom/student_result_view.html'
with open(path, 'r') as f:
    content = f.read()

# Peer data array add karna
old_data_start = "label: 'Overall Progress %'"
new_data_peer = """label: 'Student Progress %',""" # Label update

# Class average dataset insert karna
peer_dataset = """
                }, {
                    label: 'Class Average %',
                    data: [{% for avg in class_averages %}{{ avg }},{% endfor %}],
                    borderColor: '#94a3b8',
                    borderWidth: 2,
                    borderDash: [5, 5], // Dotted line
                    pointRadius: 0,
                    fill: false,
                    tension: 0.4
                """

if 'Class Average %' not in content:
    content = content.replace(old_data_start, new_data_peer)
    content = content.replace("backgroundColor: gradient", "backgroundColor: gradient" + peer_dataset)
    with open(path, 'w') as f:
        f.write(content)
    print("✅ Chart updated: Peer Comparison line added.")
else:
    print("⚠️ Chart already has Peer line.")
