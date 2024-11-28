import os
import subprocess

def generate_diagrams(project_path, output_format="png", project_name="ProjectDiagram"):
    """
    Generate UML diagrams for a Python project using Pyreverse.

    Args:
        project_path (str): Path to the root of the project.
        output_format (str): Output format for the diagrams (e.g., 'png', 'svg').
        project_name (str): Name to use for the diagrams.

    Returns:
        None
    """
    # Verify that Pyreverse is installed
    try:
        subprocess.run(["pyreverse", "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except FileNotFoundError:
        print("Error: Pyreverse is not installed. Install it with 'pip install pylint'.")
        return

    # Change directory to the project path
    os.chdir(project_path)

    # Run Pyreverse to generate class and package diagrams
    try:
        print(f"Generating diagrams for project in {project_path}...")
        subprocess.run(
            ["pyreverse", "-o", output_format, "-p", project_name, "."],
            check=True
        )
        print(f"Diagrams generated successfully in {project_path}.")
    except subprocess.CalledProcessError as e:
        print(f"Error running pyreverse: {e}")

if __name__ == "__main__":
    # Specify your project folder path
    project_folder = os.path.abspath(".")

    # Generate diagrams
    generate_diagrams(project_folder)
