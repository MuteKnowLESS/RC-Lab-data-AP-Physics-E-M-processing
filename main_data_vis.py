import os
import pandas as pd
import matplotlib.pyplot as plt

# Define constants
ROOT_PATH = "RC Lab data Raw/"
SUB_FOLDERS = ["change capacitor (1kohm, series, 3.3v)", "change resistor (47uF, series, 3.3v)", "change voltage (47uF, 1kohm, series)"]
RESISTANCES = {"change capacitor (1kohm, series, 3.3v)": [1000,1000,1000,1000,1000,1000], "change resistor (47uF, series, 3.3v)": [15000,15000,330000,330000,47,47,680,680],"change voltage (47uF, 1kohm, series)": [1000,1000,1000,1000,1000,1000,1000,1000]}

def read_data(file_path):
    """Reads CSV data into a pandas DataFrame."""
    return pd.read_csv(file_path, sep=',', header=0)

def trim_data(df):
    """Trims DataFrame to exclude rows where 'cal[0]' is zero."""
    non_zero_indices = df[df[" cal[0]"] != 0].index
    return df.loc[non_zero_indices.min():non_zero_indices.max()] if not non_zero_indices.empty else pd.DataFrame()

def combine_data_to_single_time_series(df1, df2):
    """Combines two DataFrames into a single time series by matching their time columns."""
    df1, df2 = df1[[" time", " cal[0]"]], df2[[" time", " cal[0]"]]
    df1.columns, df2.columns = [" time", " cal[0]_1"], [" time", " cal[0]_2"]
    
    # Use merge_asof to align data based on time, assuming time values are sorted
    df_combined = pd.merge_asof(df1.sort_values(" time"), df2.sort_values(" time"), on=" time", direction="nearest")
    
    return df_combined

def plot_folder_data(folder_name, combined_data_list):
    """Creates subplots for all combined data within a folder."""
    fig, axes = plt.subplots(len(combined_data_list), 1, figsize=(10, 5 * len(combined_data_list)))
    fig.suptitle(f"{folder_name}", fontsize=16)
    axes = axes if len(combined_data_list) > 1 else [axes]
    

    for ax, (file_name, df) in zip(axes, combined_data_list):
        ax.plot(df[" time"], df[" cal[0]_1"], label='Voltage Input', color='blue')
        ax.plot(df[" time"], df[" cal[0]_2"], label='Voltage Across Capacitor', color='red')
        ax.set_title(file_name.split(", Ana")[0])
        ax.set_xlabel("Time")
        ax.set_ylabel("Voltage")
        ax.legend()
        ax.grid(True)  # Enable grid lines for better readability

    #plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to include the main title

        # Adjust the spacing between subplots for better visibility
    plt.subplots_adjust(hspace=0.5)  # Adjust the vertical spacing between subplots


    plt.savefig(f"{folder_name}_plot_with_grid.png", dpi=300)  # Save with a high resolution
    
    
  
    plt.show()

def plot_folder_data_current(folder_name, combined_data_list):
    """Creates subplots for all combined data within a folder, including current (V/R) against Time."""
    fig, axes = plt.subplots(len(combined_data_list), 1, figsize=(10, 5 * len(combined_data_list)))
    fig.suptitle(f"{folder_name} Current (V(V)/R(ohm) against Time (s))", fontsize=16)
    axes = axes if len(combined_data_list) > 1 else [axes]
    
    # Get resistance values from the dictionary based on the folder name
    #resistance_values = RESISTANCES.get(folder_name, [])
    resistance_values = RESISTANCES[folder_name]
    #print(resistance_values)

    for idx, (ax, (file_name, df)) in enumerate(zip(axes, combined_data_list)):
        # Plot voltage input and voltage across capacitor
        # ax.plot(df[" time"], df[" cal[0]_1"], label='Voltage Input (V)', color='blue')
        # ax.plot(df[" time"], df[" cal[0]_2"], label='Voltage Across Capacitor (V)', color='red')

        # Calculate current (I = V / R) for each data point using the corresponding resistance
        # if resistance_values:  # Ensure we have resistance values for the folder
            # If there's more than one resistance, apply it per data point
        print(resistance_values[idx*2])
        current_input = df[" cal[0]_1"] / resistance_values[idx*2]
        current_across_cap = df[" cal[0]_2"] / resistance_values[idx*2]
            
            # Plot current
        ax.plot(df[" time"], current_input, label='Current (Input) (A)', color='green', linestyle='--')
        ax.plot(df[" time"], current_across_cap, label='Current (Across Capacitor) (A)', color='orange', linestyle='--')

        ax.set_title(file_name.split(", Ana")[0])
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Current (A)")
        ax.legend()
        ax.grid(True)  # Enable grid lines for better readability

    plt.subplots_adjust(hspace=0.5)  # Adjust the vertical spacing between subplots

    # Save the plot
    plt.savefig(f"{folder_name}_plot_with_current_with_grid.png", dpi=300)  # Save with a high resolution
    plt.show()


    # Save or show the plot
    #plt.savefig(f"{folder_name}_plot_with_current.png", dpi=300)  # Save with a high resolution
    plt.show()


def main():
    """Main function to process and plot data."""
    for folder in SUB_FOLDERS:
        folder_path = os.path.join(ROOT_PATH, folder)
        if not os.path.exists(folder_path):
            continue
        
        files = sorted(os.listdir(folder_path))
        ana7_files = {f.replace("Ana7_input.csv", ""): f for f in files if f.endswith("Ana7_input.csv")}
        ana8_files = {f.replace("Ana8_cap.csv", ""): f for f in files if f.endswith("Ana8_cap.csv")}
        
        combined_data_list = []
        
        for prefix, ana7_file in ana7_files.items():
            matching_ana8_file = ana8_files.get(prefix)
            if not matching_ana8_file:
                continue
            
            try:
                file_path_1 = os.path.join(folder_path, ana7_file)
                file_path_2 = os.path.join(folder_path, matching_ana8_file)
                
                data_1, data_2 = read_data(file_path_1), read_data(file_path_2)
                
                # Trim both data sets
                #data_1, data_2 = trim_data(data_1), trim_data(data_2)
                
                if data_1.empty or data_2.empty:
                    continue
                
                # Combine the data on time
                combined_data = combine_data_to_single_time_series(data_1, data_2)
                if not combined_data.empty:
                    combined_data_list.append((f"{ana7_file} & {matching_ana8_file}", combined_data))
            except Exception as e:
                print(f"Error processing files {ana7_file} and {matching_ana8_file}: {e}")
        
        if combined_data_list:
            plot_folder_data_current(folder, combined_data_list)
            plot_folder_data(folder, combined_data_list)

if __name__ == "__main__":
    main()
