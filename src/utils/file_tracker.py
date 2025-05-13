"""
File tracking functionality for Claude AI File Organizer.
"""

import os
import json
import datetime
from pathlib import Path


def generate_file_report(project_name, project_path, selected_files, excluded_files, output_dir):
    """
    Generate a report of which files were copied and which were excluded.
    
    Args:
        project_name (str): Name of the project
        project_path (str): Path to the project
        selected_files (list): List of selected file information
        excluded_files (list): List of excluded file information
        output_dir (str): Output directory path (should be the project directory, not the export folder)
        
    Returns:
        str: Path to the generated report file
    """
    report = {
        "project_name": project_name,
        "report_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_files_analyzed": len(selected_files) + len(excluded_files),
        "selected_files_count": len(selected_files),
        "excluded_files_count": len(excluded_files),
        "selected_files": [],
        "excluded_files": []
    }
    
    # Add selected files information
    for file_info in selected_files:
        report["selected_files"].append({
            "path": file_info["path"],
            "importance": file_info["importance"],
            "tokens": file_info.get("tokens", 0),
            "size": file_info.get("size", 0)
        })
    
    # Add excluded files information
    for file_info in excluded_files:
        report["excluded_files"].append({
            "path": file_info["path"],
            "importance": file_info["importance"],
            "size": file_info.get("size", 0),
            "reason": file_info.get("reason", "Token limit exceeded or low importance")
        })
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # Save report to JSON file in the project directory
    report_path = os.path.join(output_dir, f"{project_name}_file_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    # Create a more readable text version in the project directory
    text_report_path = os.path.join(output_dir, f"{project_name}_file_report.txt")
    with open(text_report_path, 'w', encoding='utf-8') as f:
        f.write(f"Claude AI File Organizer Report\n")
        f.write(f"==============================\n\n")
        f.write(f"Project: {project_name}\n")
        f.write(f"Report Date: {report['report_date']}\n")
        f.write(f"Total Files Analyzed: {report['total_files_analyzed']}\n")
        f.write(f"Selected Files: {report['selected_files_count']}\n")
        f.write(f"Excluded Files: {report['excluded_files_count']}\n\n")
        
        f.write(f"Selected Files:\n")
        f.write(f"---------------\n")
        # Group selected files by importance
        importance_groups = {}
        for file_info in report["selected_files"]:
            importance = file_info["importance"]
            if importance not in importance_groups:
                importance_groups[importance] = []
            importance_groups[importance].append(file_info)
        
        # Write files sorted by importance
        for importance in sorted(importance_groups.keys(), reverse=True):
            f.write(f"\nImportance Level: {importance}\n")
            for file_info in importance_groups[importance]:
                f.write(f"  - {file_info['path']} ({file_info['tokens']} tokens)\n")
        
        f.write(f"\nExcluded Files:\n")
        f.write(f"--------------\n")
        # Group excluded files by importance
        importance_groups = {}
        for file_info in report["excluded_files"]:
            importance = file_info["importance"]
            if importance not in importance_groups:
                importance_groups[importance] = []
            importance_groups[importance].append(file_info)
        
        # Write files sorted by importance
        for importance in sorted(importance_groups.keys(), reverse=True):
            f.write(f"\nImportance Level: {importance}\n")
            for file_info in importance_groups[importance]:
                f.write(f"  - {file_info['path']}\n")
    
    return text_report_path