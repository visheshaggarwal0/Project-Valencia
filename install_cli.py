import winreg

def install_cli():
    viora_path = r"C:\Users\aggar\Documents\Viora"
    print("\n[VIORA INSTALLER] Booting Windows Registry...")
    
    try:
        # Open the active User Environment Registry Key
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_ALL_ACCESS)
        
        # Safely extract the current Global PATH string
        try:
            current_path, _ = winreg.QueryValueEx(reg_key, "Path")
        except FileNotFoundError:
            current_path = ""
            
        # Ensure we don't accidentally duplicate the path
        if viora_path.lower() not in current_path.lower():
            # Clean string append
            new_path = current_path + ";" + viora_path if current_path else viora_path
            
            # Physically inject the modified string back into the Registry Database
            winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"[VIORA INSTALLER] ✅ SUCCESS! \nSuccessfully mapped {viora_path} natively into your PC!")
            print("\n*** NEXT STEPS: ***\n1. Close this terminal window entirely.\n2. Open a completely brand new Terminal (anywhere on your computer).\n3. Type: viora chat")
        else:
            print(f"[VIORA INSTALLER] ℹ️ System Link Already Established: {viora_path} is already wired into Windows.")
            
        winreg.CloseKey(reg_key)
        
    except Exception as e:
        print(f"[VIORA INSTALLER] ❌ CRITICAL ERROR: Windows blocked the registry update: {str(e)}")
        print("Please run this terminal as Administrator if it continues blocking you.")

if __name__ == "__main__":
    install_cli()
