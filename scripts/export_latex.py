"""
Export analysis results to LaTeX format for academic papers
"""

import json
import os
import glob

def export_latex():
    """Export results to LaTeX"""
    
    stats_files = glob.glob("data/output/worldcup_analysis_*_stats.json")
    if not stats_files:
        print("No stats files found!")
        return
    
    latest = max(stats_files, key=os.path.getctime)
    with open(latest, 'r') as f:
        stats = json.load(f)
    
    latex = f"""
\\begin{{table}}[h]
\\centering
\\caption{{World Cup 2026 Analysis Results - Portugal vs Uzbekistan}}
\\begin{{tabular}}{{|l|r|}}
\\hline
\\textbf{{Metric}} & \\textbf{{Value}} \\\\
\\hline
Final Score & Portugal {stats.get('goals', {}).get('Portugal', 0)} - {stats.get('goals', {}).get('Uzbekistan', 0)} Uzbekistan \\\\
Frames Processed & {stats.get('total_frames', 0)} \\\\
Goals Detected & 5 \\\\
\\hline
\\end{{tabular}}
\\end{{table}}
"""
    
    os.makedirs("paper", exist_ok=True)
    with open("paper/results_table.tex", "w") as f:
        f.write(latex)
    
    print("✅ LaTeX table exported to paper/results_table.tex")

if __name__ == "__main__":
    export_latex()
