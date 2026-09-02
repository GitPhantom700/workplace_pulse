import re

html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# I want to delete the block starting from the second <div class="col-span-2"> (Project ID) 
# until the end of the col-span-1 (Client Secret) div.

# Let's use a regex to find the Project ID block to Client Secret block and remove it.

pattern = re.compile(
    r'(<div class="col-span-2">\s*<label class="block text-\[10px\] font-bold text-slate-700 uppercase mb-1 flex justify-between"><span>Project ID</span>.*?</label>.*?</div>\s*</div>\s*'
    r'<div class="col-span-1">\s*<label class="block text-\[10px\] font-bold text-slate-700 uppercase mb-1 flex justify-between"><span>OAuth Client ID</span>.*?</label>.*?</div>\s*</div>\s*'
    r'<div class="col-span-1">\s*<label class="block text-\[10px\] font-bold text-slate-700 uppercase mb-1 flex justify-between"><span>Client Secret</span>.*?</label>.*?</div>\s*</div>)',
    re.DOTALL
)

new_content = pattern.sub('', content)

if content != new_content:
    with open(html_path, 'w') as f:
        f.write(new_content)
    print("Deleted the simulated fields.")
else:
    print("Pattern not found!")
