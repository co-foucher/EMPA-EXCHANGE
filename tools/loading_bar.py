# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 10:59:07 2024

@author: cofo

"""
import sys


def main(current, total, bar_length=30):
    """
    Displays or updates a loading bar animation on the console based on the current progress.

    Parameters:
    - current: The current progress value.
    - total: The total value corresponding to 100% progress.
    - bar_length: The length of the loading bar in characters.
    """
    # Calculate the percentage of progress
    progress = (current+1) / total
    
    # Ensure the progress does not exceed 100%
    progress = min(1.0, max(0.0, progress))
    
    # Calculate the number of filled positions in the bar
    filled_length = int(bar_length * progress)
    
    # Create the bar string
    bar = "#" * filled_length + "-" * (bar_length - filled_length)
    
    # Print the loading bar with the current percentage
    sys.stdout.write(f"\rProgress: [{bar}] {int(progress * 100)}%")
    #sys.stdout.flush()

    # Print a newline when progress reaches 100%
    if progress == 1.0:
        print()  # Move to a new line


if __name__ == "__main__":
    print("this script is meant to be imported as a module, not run as a standalone.")