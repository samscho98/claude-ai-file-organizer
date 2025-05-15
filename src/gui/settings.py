"""
Settings GUI for Claude AI File Organizer.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import configparser
from pathlib import Path
import subprocess

# Ensure the proper module path is set
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))  # Go up two levels to project root
sys.path.insert(0, project_root)

# Now import project modules
from src.utils.config import load_config, create_default_config
from src.utils.ignore import create_default_ignore


class SettingsGUI:
    """GUI for Claude AI File Organizer settings."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Claude AI File Organizer Settings")
        self.root.geometry("650x600")
        self.root.resizable(True, True)
        
        # Load config or create default if not exists
        self.config_path = os.path.join(project_root, "config.ini")
        if not os.path.exists(self.config_path):
            create_default_config(self.config_path)
        
        self.config = load_config(self.config_path)
        
        # Create ignore file if not exists
        ignore_path = os.path.join(project_root, self.config['settings'].get('ignore', '.ignore'))
        if not os.path.exists(ignore_path):
            create_default_ignore(ignore_path)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        general_tab = ttk.Frame(notebook)
        importance_tab = ttk.Frame(notebook)
        api_tab = ttk.Frame(notebook)
        
        notebook.add(general_tab, text="General Settings")
        notebook.add(importance_tab, text="File Importance")
        notebook.add(api_tab, text="API Settings")
        
        # General Settings Tab
        self.create_general_settings(general_tab)
        
        # File Importance Tab
        self.create_importance_settings(importance_tab)
        
        # API Settings Tab
        self.create_api_settings(api_tab)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Save Button
        save_button = ttk.Button(buttons_frame, text="Save Settings", command=self.save_settings)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        # Run Button
        run_button = ttk.Button(buttons_frame, text="Save & Run Organizer", command=self.run_organizer)
        run_button.pack(side=tk.RIGHT, padx=5)
    

    def create_general_settings(self, parent):
        """Create general settings widgets."""
        # Create frame with padding
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Project Path
        ttk.Label(frame, text="Project Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        path_frame = ttk.Frame(frame)
        path_frame.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        self.project_path_var = tk.StringVar(value=self.config['settings'].get('path', ''))
        project_path_entry = ttk.Entry(path_frame, textvariable=self.project_path_var, width=40)
        project_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(path_frame, text="Browse...", command=self.browse_project_path)
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # Output Directory
        ttk.Label(frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        output_dir_frame = ttk.Frame(frame)
        output_dir_frame.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        self.output_dir_var = tk.StringVar(value=self.config['settings'].get('output_dir', 'output'))
        output_dir_entry = ttk.Entry(output_dir_frame, textvariable=self.output_dir_var, width=40)
        output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        output_dir_browse = ttk.Button(output_dir_frame, text="Browse...", command=self.browse_output_dir)
        output_dir_browse.pack(side=tk.RIGHT, padx=5)
        
        # Ignore File
        ttk.Label(frame, text="Ignore File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ignore_frame = ttk.Frame(frame)
        ignore_frame.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        self.ignore_file_var = tk.StringVar(value=self.config['settings'].get('ignore', '.ignore'))
        ignore_file_entry = ttk.Entry(ignore_frame, textvariable=self.ignore_file_var, width=40)
        ignore_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ignore_browse = ttk.Button(ignore_frame, text="Browse...", command=self.browse_ignore_file)
        ignore_browse.pack(side=tk.RIGHT, padx=5)
        
        # Important Files Path
        ttk.Label(frame, text="Important Files List:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        important_files_frame = ttk.Frame(frame)
        important_files_frame.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Determine the default important files path
        default_file = 'important_files.txt'
        default_path = os.path.join(project_root, default_file)
        
        if os.path.exists(default_path):
            # If the file exists in project root, use it (relative path form)
            important_files_path = default_file
        else:
            # Otherwise use whatever is in the config
            important_files_path = self.config['settings'].get('important_files_path', default_file)
            
        print(f"Important files path (init): {important_files_path}")
            
        # Create the entry directly with a plain string value (not using StringVar)
        self.important_files_entry = ttk.Entry(important_files_frame, width=40)
        self.important_files_entry.insert(0, important_files_path)  # Insert the text directly
        self.important_files_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        important_files_browse = ttk.Button(important_files_frame, text="Browse...", 
                                            command=self.browse_important_files)
        important_files_browse.pack(side=tk.RIGHT, padx=5)
        
        # Max Tokens
        ttk.Label(frame, text="Max Tokens:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.max_tokens_var = tk.StringVar(value=self.config['settings'].get('max_tokens', '60000'))
        max_tokens_entry = ttk.Entry(frame, textvariable=self.max_tokens_var, width=40)
        max_tokens_entry.grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # Generate Structure
        ttk.Label(frame, text="Generate Structure:").grid(row=5, column=0, sticky=tk.W, pady=5)
        
        self.generate_structure_var = tk.BooleanVar(value=self.config['settings'].getboolean('generate_structure', True))
        generate_structure_check = ttk.Checkbutton(frame, variable=self.generate_structure_var)
        generate_structure_check.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Generate README
        ttk.Label(frame, text="Generate README:").grid(row=6, column=0, sticky=tk.W, pady=5)
        
        self.generate_readme_var = tk.BooleanVar(value=self.config['settings'].getboolean('generate_readme', True))
        generate_readme_check = ttk.Checkbutton(frame, variable=self.generate_readme_var)
        generate_readme_check.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # Open Output Folder After Processing
        ttk.Label(frame, text="Show in File Explorer:").grid(row=7, column=0, sticky=tk.W, pady=5)
        
        self.open_output_var = tk.BooleanVar(value=self.config['settings'].getboolean('open_output_folder', True))
        open_output_check = ttk.Checkbutton(frame, variable=self.open_output_var)
        open_output_check.grid(row=7, column=1, sticky=tk.W, pady=5)
        
        # Configure grid to expand properly
        frame.columnconfigure(1, weight=1)
    
    def create_importance_settings(self, parent):
        """Create file importance settings widgets."""
        # Create frame with padding
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Important Formats
        ttk.Label(frame, text="Important File Formats:").grid(row=0, column=0, sticky=tk.NW, pady=5)
        
        self.important_formats_var = tk.StringVar(value=self.config['file_importance'].get('important_formats', ''))
        important_formats_text = tk.Text(frame, height=4, width=40, wrap=tk.WORD)
        important_formats_text.grid(row=0, column=1, sticky=tk.EW, pady=5)
        important_formats_text.insert(tk.END, self.important_formats_var.get())
        self.important_formats_text = important_formats_text
        
        ttk.Label(frame, text="(Comma-separated list of file extensions, e.g. .py,.md,.txt)").grid(row=1, column=1, sticky=tk.W, pady=0)
        
        # Important Files
        ttk.Label(frame, text="Important Files:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        
        self.important_files_var = tk.StringVar(value=self.config['file_importance'].get('important_files', ''))
        important_files_text = tk.Text(frame, height=4, width=40, wrap=tk.WORD)
        important_files_text.grid(row=2, column=1, sticky=tk.EW, pady=5)
        important_files_text.insert(tk.END, self.important_files_var.get())
        self.important_files_text = important_files_text
        
        ttk.Label(frame, text="(Comma-separated list of filenames, e.g. README.md,setup.py)").grid(row=3, column=1, sticky=tk.W, pady=0)
        
        # Important Paths
        ttk.Label(frame, text="Important Paths:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        
        self.important_paths_var = tk.StringVar(value=self.config['file_importance'].get('important_paths', ''))
        important_paths_text = tk.Text(frame, height=4, width=40, wrap=tk.WORD)
        important_paths_text.grid(row=4, column=1, sticky=tk.EW, pady=5)
        important_paths_text.insert(tk.END, self.important_paths_var.get())
        self.important_paths_text = important_paths_text
        
        ttk.Label(frame, text="(Comma-separated list of directory paths, e.g. src/,docs/)").grid(row=5, column=1, sticky=tk.W, pady=0)
        
        # Configure grid to expand properly
        frame.columnconfigure(1, weight=1)
    
    def create_api_settings(self, parent):
        """Create API settings widgets."""
        # Create frame with padding
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Extract Endpoints
        ttk.Label(frame, text="Extract API Endpoints:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.extract_endpoints_var = tk.BooleanVar(value=self.config['api_settings'].getboolean('extract_endpoints', False))
        extract_endpoints_check = ttk.Checkbutton(frame, variable=self.extract_endpoints_var)
        extract_endpoints_check.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Help text
        ttk.Label(
            frame, 
            text="When enabled, API endpoints will be saved to [project_name]_endpoints.json in the output directory",
            wraplength=350
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Examples section
        ttk.Label(frame, text="Pattern Examples:").grid(row=2, column=0, sticky=tk.W, pady=(20, 5))
        
        # Show example patterns in a readonly text box
        example_text = tk.Text(frame, height=10, width=60, wrap=tk.WORD)
        example_text.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=5, padx=5)
        example_text.insert(tk.END, 
                           "The API endpoint extraction will find patterns like:\n\n"
                           "Flask/FastAPI:\n"
                           "  @app.route('/api/users')\n"
                           "  @app.get('/api/products')\n"
                           "  @blueprint.route('/admin/dashboard')\n\n"
                           "Express.js:\n"
                           "  app.get('/api/users', ...)\n"
                           "  router.post('/api/login', ...)\n\n"
                           "Spring (Java):\n"
                           "  @RequestMapping(\"/api/users\")\n"
                           "  @GetMapping(\"/api/products\")")
        example_text.config(state=tk.DISABLED, bg="#f0f0f0")
        
        # Configure grid to expand properly
        frame.columnconfigure(1, weight=1)
    
    def browse_project_path(self):
        """Open directory browser for project path."""
        directory = filedialog.askdirectory(
            initialdir=self.project_path_var.get() or os.path.expanduser("~"),
            title="Select Project Directory"
        )
        if directory:
            self.project_path_var.set(directory)
    
    def browse_output_dir(self):
        """Open directory browser for output directory."""
        directory = filedialog.askdirectory(
            initialdir=self.output_dir_var.get() or os.path.join(project_root, "output"),
            title="Select Output Directory"
        )
        if directory:
            self.output_dir_var.set(directory)
    
    def browse_ignore_file(self):
        """Open file browser for ignore file."""
        filename = filedialog.askopenfilename(
            initialdir=os.path.dirname(self.ignore_file_var.get()) or project_root,
            title="Select Ignore File",
            filetypes=(("Ignore files", ".ignore"), ("All files", "*.*"))
        )
        if filename:
            self.ignore_file_var.set(filename)
    
    def browse_important_files(self):
        """Open file browser for important files list."""
        # Get initial directory - either the directory of the current value or project root
        current_value = self.important_files_entry.get()
        if current_value and os.path.dirname(current_value):
            if os.path.isabs(current_value):
                initial_dir = os.path.dirname(current_value)
            else:
                initial_dir = os.path.dirname(os.path.join(project_root, current_value))
        else:
            initial_dir = project_root
            
        filename = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Select Important Files List",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        
        if filename:
            print(f"Selected file: {filename}")
            
            # Convert to relative path if within project root
            if filename.startswith(project_root):
                rel_path = os.path.relpath(filename, project_root)
                self.important_files_entry.delete(0, tk.END)
                self.important_files_entry.insert(0, rel_path)
                print(f"Using relative path: {rel_path}")
            else:
                # Use absolute path if outside project root
                self.important_files_entry.delete(0, tk.END)
                self.important_files_entry.insert(0, filename)
                print(f"Using absolute path: {filename}")

    def get_text_content(self, text_widget):
        """Get content from a Text widget."""
        return text_widget.get("1.0", tk.END).strip()
    
    def save_settings(self):
        """Save settings to config file."""
        try:
            # Update config object with current values
            # General Settings
            self.config['settings']['path'] = self.project_path_var.get()
            self.config['settings']['output_dir'] = self.output_dir_var.get()
            self.config['settings']['ignore'] = self.ignore_file_var.get()
            
            # Get value directly from entry widget
            self.config['settings']['important_files_path'] = self.important_files_entry.get()
            
            self.config['settings']['max_tokens'] = self.max_tokens_var.get()
            self.config['settings']['generate_structure'] = str(self.generate_structure_var.get())
            self.config['settings']['generate_readme'] = str(self.generate_readme_var.get())
            self.config['settings']['open_output_folder'] = str(self.open_output_var.get())
            
            # File Importance Settings
            self.config['file_importance']['important_formats'] = self.get_text_content(self.important_formats_text)
            self.config['file_importance']['important_files'] = self.get_text_content(self.important_files_text)
            self.config['file_importance']['important_paths'] = self.get_text_content(self.important_paths_text)
            
            # API Settings
            self.config['api_settings']['extract_endpoints'] = str(self.extract_endpoints_var.get())
            # We don't need to save an endpoint path anymore as it's automatically generated
            if 'endpoint_path' in self.config['api_settings']:
                self.config['api_settings']['endpoint_path'] = ''
            
            # Save to file
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
            
            messagebox.showinfo("Success", "Settings saved successfully.")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {e}")
            return False
    
    def open_output_folder(self):
        """Open the output folder in the system's file explorer."""
        output_dir = self.output_dir_var.get()
        if os.path.exists(output_dir):
            try:
                if sys.platform == 'win32':
                    os.startfile(output_dir)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.call(['open', output_dir])
                else:  # Linux
                    subprocess.call(['xdg-open', output_dir])
            except Exception as e:
                messagebox.showwarning("Warning", f"Could not open output folder: {e}")
    
    def run_organizer(self):
        """Save settings and run the organizer."""
        if self.save_settings():
            try:
                # Create a direct command to run the main script from the correct directory
                import subprocess
                
                # Get the main.py script path
                main_script = os.path.join(project_root, 'src', 'main.py')
                
                # Use the current Python executable
                python_executable = sys.executable
                
                # Set the working directory to the project root
                working_dir = project_root
                
                messagebox.showinfo("Running", "Starting the organizer...\nThis window will close.")
                self.root.destroy()
                
                # Run the organizer with proper environment
                process = subprocess.Popen(
                    [python_executable, main_script],
                    cwd=working_dir,
                    env=dict(os.environ, PYTHONPATH=working_dir)
                )
                
                # Wait for the process to complete
                process.wait()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error running organizer: {e}")


def main():
    """Main function to run the settings GUI."""
    root = tk.Tk()
    app = SettingsGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()