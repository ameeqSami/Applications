import os
import re

template_dir = r"d:\Repos\Applications\templates"

replacements = [
    # Fonts
    (r"https://fonts\.googleapis\.com/css2\?family=JetBrains\+Mono:wght@400;500;700&display=swap", 
     r"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"),
    (r"font-family:\s*'JetBrains Mono',\s*monospace;", r"font-family: 'Inter', sans-serif;"),
    (r"mono:\s*\['\"JetBrains Mono\"',\s*'monospace'\],?", r"sans: ['\"Inter\"', 'sans-serif'],"),
    
    # Tailwind config
    (r"bg:\s*'#0A0A0B',", r"bg: '#f8fafc',"),
    (r"surface:\s*'rgba\(255,\s*255,\s*255,\s*0\.03\)',", r"surface: '#ffffff',"),
    (r"accent:\s*'#8B5CF6',", r"accent: '#2563eb',"),
    (r"acid:\s*'#A8FF35',", r"acid: '#0ea5e9',"),

    # Body background in style
    (r"body\s*\{\s*background-color:\s*#0A0A0B;\s*color:\s*#ffffff;", r"body { background-color: #f8fafc; color: #0f172a;"),
    
    # Glass Widget Style
    (r"\.glass-widget\s*\{\s*background-color:\s*rgba\(255,\s*255,\s*255,\s*0\.03\);\s*backdrop-filter:\s*blur\(15px\);\s*-webkit-backdrop-filter:\s*blur\(15px\);\s*border:\s*1px\s*solid\s*rgba\(255,\s*255,\s*255,\s*0\.1\);\s*border-radius:\s*1rem;\s*padding:\s*(.*?);\s*\}", 
     r".glass-widget {\n            background-color: #ffffff;\n            border: 1px solid #e2e8f0;\n            border-radius: 0.75rem;\n            padding: \1;\n            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);\n        }"),

    # Progress Ring Style
    (r"stroke:\s*#A8FF35;", r"stroke: #2563eb;"),
    (r"stroke:\s*rgba\(255,\s*255,\s*255,\s*0\.1\);", r"stroke: #e2e8f0;"),

    # Scrollbar
    (r"::-webkit-scrollbar-thumb\s*\{\s*background:\s*rgba\(255,\s*255,\s*255,\s*0\.2\);", r"::-webkit-scrollbar-thumb {\n            background: #cbd5e1;"),
    (r"::-webkit-scrollbar-thumb:hover\s*\{\s*background:\s*rgba\(255,\s*255,\s*255,\s*0\.3\);", r"::-webkit-scrollbar-thumb:hover {\n            background: #94a3b8;"),

    # Urgent Glow
    (r"\.urgent-glow\s*\{\s*box-shadow:\s*0\s*0\s*15px\s*rgba\(139,\s*92,\s*246,\s*0\.4\);\s*border-color:\s*rgba\(139,\s*92,\s*246,\s*0\.6\);\s*\}", 
     r".urgent-glow {\n            box-shadow: 0 0 0 2px #ef4444;\n            border-color: #ef4444;\n        }"),

    # Input style for login/register
    (r"input\s*\{\s*background-color:\s*rgba\(255,\s*255,\s*255,\s*0\.05\);\s*border:\s*1px\s*solid\s*rgba\(255,\s*255,\s*255,\s*0\.1\);\s*color:\s*white;\s*transition:\s*border-color\s*0\.2s;\s*\}",
     r"input {\n            background-color: #ffffff;\n            border: 1px solid #e2e8f0;\n            color: #0f172a;\n            transition: border-color 0.2s, box-shadow 0.2s;\n        }"),
    (r"input:focus\s*\{\s*outline:\s*none;\s*border-color:\s*#8B5CF6;\s*\}",
     r"input:focus {\n            outline: none;\n            border-color: #2563eb;\n            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);\n        }"),

    # Tailwind Utility Classes Replacements
    (r'bg-\[\#0A0A0B\]', r'bg-slate-50'),
    (r'text-white/80', r'text-slate-800'),
    (r'text-white/70', r'text-slate-600'),
    (r'text-white/60', r'text-slate-500'),
    (r'text-white/50', r'text-slate-500'),
    (r'text-white/30', r'text-slate-400'),
    (r'text-white/20', r'text-slate-300'),
    (r'hover:text-white', r'hover:text-slate-900'),
    (r'text-white', r'text-slate-900'),
    
    (r'border-white/5', r'border-slate-100'),
    (r'border-white/10', r'border-slate-200'),
    (r'border-white/20', r'border-slate-300'),
    (r'border-white/30', r'border-slate-300'),
    (r'border-white/50', r'border-slate-400'),
    
    (r'bg-white/5', r'bg-slate-50'),
    (r'bg-white/10', r'bg-slate-100'),
    (r'bg-white/20', r'bg-slate-200'),
    (r'hover:bg-white/5', r'hover:bg-slate-100'),
    (r'hover:bg-white/10', r'hover:bg-slate-100'),
    
    (r'bg-black/20', r'bg-white'),
    (r'bg-black/40', r'bg-slate-50'),
    (r'bg-black/60', r'bg-slate-900/40'), # Keep backdrop dark

    (r'placeholder-white/30', r'placeholder-slate-400'),
    (r'placeholder-white/50', r'placeholder-slate-500'),
    
    # Specific elements
    (r'text-brand-acid', r'text-brand-accent'),
    (r'bg-brand-acid', r'bg-brand-accent'),
    (r'border-brand-acid', r'border-brand-accent'),
    (r'hover:text-brand-acid', r'hover:text-brand-accent'),
    
    # Terminology changes
    (r'SYS\.TASK_MANAGER', r'Academic Task Manager'),
    (r'SYS\.AI Chat', r'AI Assistant'),
    
    # Other specifics
    (r'tracking-widest', r'tracking-wide'),
]

for filename in os.listdir(template_dir):
    if filename.endswith(".html"):
        path = os.path.join(template_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        for old, new in replacements:
            content = re.sub(old, new, content)
            
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

print("Migration completed.")
