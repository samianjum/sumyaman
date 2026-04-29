import os

def patch_profile_system():
    file_path = 'mobile_app.py'
    
    with open(file_path, 'r') as f:
        content = f.read()

    # 1. Update Profile UI (HTML)
    new_profile_html = '''
            <div id="page-profile" class="hidden p-4 pb-24 overflow-y-auto h-full">
                <div class="w-full bg-[#112240] rounded-3xl p-6 mb-4 shadow-xl flex flex-col items-center border border-gray-700">
                    <div class="relative group">
                        <div id="p-img-container" class="w-24 h-24 rounded-full border-4 border-[#2F80ED] overflow-hidden bg-[#1d3557] flex items-center justify-center text-3xl font-bold text-white shadow-2xl">
                            <span id="p-initials">{{ user.full_name[:1].upper() }}</span>
                        </div>
                        <button onclick="document.getElementById('p-upload').click()" class="absolute bottom-0 right-0 bg-[#2F80ED] p-2 rounded-full shadow-lg border-2 border-[#112240] hover:scale-110 transition-transform">
                            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                        </button>
                        <input type="file" id="p-upload" class="hidden" accept="image/*" onchange="uploadProfilePic(this)">
                    </div>
                    <h2 class="text-white text-xl font-bold mt-4 mb-1">{{ user.full_name.title() }}</h2>
                    <span class="px-3 py-1 bg-[#2F80ED]/20 text-[#2F80ED] rounded-full text-xs font-black uppercase tracking-wider">
                        {{ user.role }} • {{ user.student_class if user.role == 'Student' else user.designation or 'Faculty' }}-{{ user.student_section if user.role == 'Student' else '' }}
                    </span>
                </div>

                <div class="space-y-4">
                    <div class="bg-[#112240] rounded-2xl p-5 border border-gray-800">
                        <div class="flex items-center space-x-3 mb-4 text-[#2F80ED]">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 14l9-5-9-5-9 5 9 5z"></path><path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"></path></svg>
                            <h4 class="font-bold text-gray-300">Academic Details</h4>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            {% if user.role == 'Student' %}
                            <div><p class="text-gray-500 text-xs">Roll Number</p><p class="text-gray-200 font-medium">{{ user.roll_number }}</p></div>
                            <div><p class="text-gray-500 text-xs">Section/Wing</p><p class="text-gray-200 font-medium">{{ user.student_section }} ({{ user.wing }})</p></div>
                            {% else %}
                            <div><p class="text-gray-500 text-xs">Department</p><p class="text-gray-200 font-medium">{{ user.assigned_wing or 'General' }}</p></div>
                            <div><p class="text-gray-500 text-xs">Status</p><p class="text-gray-200 font-medium">{{ 'Class Teacher' if user.is_class_teacher else 'Subject Teacher' }}</p></div>
                            {% endif %}
                        </div>
                    </div>

                    <div class="bg-[#112240] rounded-2xl border border-gray-800 overflow-hidden">
                        <button onclick="document.getElementById('personal-info').classList.toggle('hidden')" class="w-full p-5 flex justify-between items-center text-gray-300 font-bold">
                            <span class="flex items-center space-x-3">
                                <svg class="w-5 h-5 text-[#2F80ED]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                                <span>Personal Information</span>
                            </span>
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 9l-7 7-7-7"></path></svg>
                        </button>
                        <div id="personal-info" class="hidden px-5 pb-5 grid grid-cols-1 gap-3 border-t border-gray-800 pt-4">
                            {% if user.role == 'Student' %}
                            <div><p class="text-gray-500 text-xs">Father Name</p><p class="text-gray-200">{{ user.father_name }}</p></div>
                            <div><p class="text-gray-500 text-xs">Date of Birth</p><p class="text-gray-200">{{ user.dob }}</p></div>
                            <div><p class="text-gray-500 text-xs">Parent Contact</p><p class="text-gray-200">{{ user.parents_phone }}</p></div>
                            {% else %}
                            <div><p class="text-gray-500 text-xs">CNIC</p><p class="text-gray-200">{{ user.cnic }}</p></div>
                            <div><p class="text-gray-500 text-xs">Phone</p><p class="text-gray-200">{{ user.contact }}</p></div>
                            {% endif %}
                            <div><p class="text-gray-500 text-xs">Address</p><p class="text-gray-200 text-sm italic">{{ user.address }}</p></div>
                        </div>
                    </div>

                    <div class="pt-4">
                        <button onclick="safeLogout(event)" class="w-full bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/30 py-4 rounded-2xl font-black text-sm flex items-center justify-center space-x-2 transition-all">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                            <span>LOGOUT ACCOUNT</span>
                        </button>
                    </div>

                    <p class="text-center text-gray-600 text-[10px] font-bold tracking-widest uppercase mt-4">Powered by AXIS • APS OKARA</p>
                </div>
            </div>
    '''
    
    # Injection Logic: Replace the old page-profile div
    import re
    content = re.sub(r'<div id="page-profile".*?</div>\s*</div>', new_profile_html + '\n            </div>', content, flags=re.DOTALL)

    # 2. Update JS: Add Image Upload Logic
    js_logic = '''
    window.uploadProfilePic = async function(input) {
        if (!input.files || !input.files[0]) return;
        const file = input.files[0];
        if (file.size > 2 * 1024 * 1024) { showToast("File too large (Max 2MB)", "error"); return; }

        const formData = new FormData();
        formData.append('pic', file);

        showToast("Uploading...", "info");
        try {
            const res = await fetch('/api/update-profile-pic', { method: 'POST', body: formData });
            const data = await res.json();
            if (data.success) {
                location.reload();
            } else {
                showToast("Upload failed", "error");
            }
        } catch (e) { console.error(e); }
    };
    '''
    # Append JS logic before the closing script tag
    content = content.replace('</script>', js_logic + '\n</script>')

    # 3. Add Backend Route for Upload
    backend_route = '''
@app.route('/api/update-profile-pic', methods=['POST'])
@login_required
def update_profile_pic():
    if 'pic' not in request.files: return jsonify({"success": False}), 400
    file = request.files['pic']
    u = session['user']
    user_id = u['id']
    role = u['role']
    
    filename = f"{role.lower()}_{user_id}.jpg"
    save_path = os.path.join('static/uploads/profile_pics', filename)
    file.save(save_path)
    
    return jsonify({"success": True})
'''
    content += backend_route

    with open(file_path, 'w') as f:
        f.write(content)
    print("Success: Profile System patched successfully!")

if __name__ == "__main__":
    patch_profile_system()
