# dependency_setup.py - Safe version that prevents crashes
import logging
import sys
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('safe_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_setup():
    """Main setup function using the minimal safe approach"""
    try:
        logger.info("Starting safe Mailreader setup process")
        
        # Import the minimal GUI module
        from minimal_setup_gui import run_setup as run_minimal_setup
        
        # Run the minimal setup
        result = run_minimal_setup()
        
        logger.info(f"Safe setup completed with result: {result}")
        return result
        
    except ImportError as e:
        logger.error(f"Failed to import minimal setup modules: {e}")
        print(f"Error: Could not import setup modules: {e}")
        print("Make sure these files exist:")
        print("- dependency_setup.py")
        print("- minimal_setup_gui.py") 
        print("- completely_isolated_installer.py")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error during safe setup: {e}")
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Test the safe setup
    print("Mailreader Safe Setup Starting...")
    result = run_setup()
    print(f"Setup completed: {result}")
    
    if result:
        print("Setup successful! Your application should work with basic functionality.")
    else:
        print("Setup failed or was cancelled. Check the safe_setup.log file for details.")