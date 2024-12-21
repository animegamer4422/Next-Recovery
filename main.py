import os
import sys
import subprocess
import ctypes
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAction, QMessageBox
)
import qdarkstyle


class DiskInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Disk Info Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Add menu for theme switching
        menubar = self.menuBar()
        theme_menu = menubar.addMenu("Theme")

        light_action = QAction("Light Mode", self)
        dark_action = QAction("Dark Mode", self)
        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)

        light_action.triggered.connect(self.apply_light_mode)
        dark_action.triggered.connect(self.apply_dark_mode)

        # Main layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Table widget
        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)

        # Initialize table
        self.initialize_table()

    def initialize_table(self):
        # Get disk information
        disks = self.get_disks()

        # Handle no disk case
        if not disks:
            self.show_error("No disks found or failed to fetch disk information.")
            return

        # Configure table
        self.table_widget.setRowCount(len(disks))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Model", "Type", "Partition", "Size"])

        # Enable interactive resizing for columns
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)

        # Populate table
        for row, disk in enumerate(disks):
            self.table_widget.setItem(row, 0, QTableWidgetItem(disk["id"]))
            self.table_widget.setItem(row, 1, QTableWidgetItem(disk["model"]))
            self.table_widget.setItem(row, 2, QTableWidgetItem(disk["type"]))
            self.table_widget.setItem(row, 3, QTableWidgetItem(disk["partition"]))
            self.table_widget.setItem(row, 4, QTableWidgetItem(disk["size"]))

    def get_disks(self):
        """
        Uses ntfstool to fetch available disks information.
        Parses the output and returns it as a list of dictionaries.
        """
        ntfstool_path = os.path.join(os.getcwd(), "ntfstool.x64.exe")

        try:
            # Run ntfstool with the "info" command
            result = subprocess.run(
                [ntfstool_path, "info"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                raise Exception(f"Error: {result.stderr}")

            # Log raw output for debugging
            print("Raw output from ntfstool (info):")
            print(result.stdout)

            # Parse the output
            disks = []
            in_disks_section = False
            for line in result.stdout.splitlines():
                # Skip header or irrelevant sections
                if "Disks:" in line:
                    in_disks_section = True
                    continue
                if in_disks_section and line.strip().startswith("+"):
                    continue  # Skip table borders
                if in_disks_section and "|" in line:
                    # Example line: "| 0  | Samsung SSD 970  | Fixed SSD     | GPT       | 1000204886016 (931.51 GiBs) |"
                    parts = [x.strip() for x in line.split("|")[1:-1]]
                    if len(parts) == 5:
                        disks.append({
                            "id": parts[0],
                            "model": parts[1],
                            "type": parts[2],
                            "partition": parts[3],
                            "size": parts[4],
                        })

            return disks
        except Exception as e:
            print(f"Failed to fetch disks: {e}")
            return []

    def show_error(self, message):
        """
        Display an error message to the user.
        """
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(message)
        error_dialog.exec_()

    def apply_light_mode(self):
        """
        Switch to light mode.
        """
        app.setStyleSheet("")  # Default PyQt5 light mode

    def apply_dark_mode(self):
        """
        Switch to dark mode using QDarkStyle.
        """
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())


def is_admin():
    """
    Checks if the script is running with administrator privileges.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def elevate():
    """
    Relaunch the script with administrator privileges.
    """
    if not is_admin():
        print("Requesting admin privileges...")
        # Relaunch the script with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()


# Main application entry point
if __name__ == "__main__":
    # Ensure the script is run with administrator privileges
    elevate()

    app = QApplication(sys.argv)
    window = DiskInfoApp()

    # Apply default dark mode
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    window.show()
    sys.exit(app.exec_())
