import os
import re

dir_path = r'd:\Repos\Applications\templates'
for filename in os.listdir(dir_path):
    if filename.endswith('.html'):
        filepath = os.path.join(dir_path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace fonts
        content = content.replace('family=JetBrains+Mono:wght@400;500;700', 'family=Inter:wght@400;500;600;700')
        
        # Replace Tailwind config
        content = re.sub(r'tailwind\.config\s*=\s*\{.*?\};?', '''tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        brand: {
                            bg: '#f8fafc',
                            surface: '#ffffff',
                            accent: '#2563eb',
                            acid: '#0284c7',
                        }
                    },
                    fontFamily: {
                        sans: ['"Inter"', 'sans-serif'],
                        mono: ['"Inter"', 'sans-serif'],
                    }
                }
            }
        }''', content, flags=re.DOTALL)

        # Replace style blocks
        content = re.sub(r'<style>.*?</style>', '''<style>
        body {
            background-color: #f8fafc;
            color: #0f172a;
            font-family: 'Inter', sans-serif;
        }

        .glass-widget {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        }

        .urgent-glow {
            box-shadow: 0 0 15px rgba(37, 99, 235, 0.2);
            border-color: rgba(37, 99, 235, 0.4);
        }

        /* Progress Ring */
        .progress-ring__circle {
            transition: stroke-dashoffset 0.35s;
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
            stroke: #2563eb;
        }
        
        .progress-ring__background {
            stroke: #e2e8f0;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: transparent; 
        }
        ::-webkit-scrollbar-thumb {
            background: #cbd5e1; 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8; 
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #2563eb !important;
            box-shadow: 0 0 0 1px #2563eb;
        }
    </style>''', content, flags=re.DOTALL)

        # Basic replacements
        replacements = {
            'text-brand-acid': 'text-brand-accent',
            'bg-[#0A0A0B]': 'bg-white',
            'text-white': 'text-slate-800',
            'text-white/20': 'text-slate-400',
            'border-white/10': 'border-slate-200',
            'border-white/20': 'border-slate-200',
            'border-white/30': 'border-slate-300',
            'bg-white/5': 'bg-slate-50',
            'bg-white/10': 'bg-slate-100',
            'hover:bg-white/10': 'hover:bg-slate-100',
            'hover:bg-white/5': 'hover:bg-slate-50',
            'bg-black/20': 'bg-white',
            'bg-black/60': 'bg-slate-900/60',
            'placeholder-white/30': 'placeholder-slate-400',
            'text-white/30': 'text-slate-400',
            'text-white/50': 'text-slate-500',
            'text-white/70': 'text-slate-600',
            'text-white/80': 'text-slate-700',
            'hover:text-white': 'hover:text-slate-900',
            'border-brand-acid': 'border-brand-accent',
            'bg-brand-acid/20': 'bg-blue-100',
            'SYS.TASK_MANAGER': 'Academic Dashboard',
            'SYS.AI Chat': 'Assistant Chat',
            'JetBrains Mono': 'Inter'
        }
        
        for k, v in replacements.items():
            content = content.replace(k, v)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
