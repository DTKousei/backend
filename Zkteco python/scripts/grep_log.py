import sys

def grep_file():
    filename = "debug_calc_2025.txt"
    keywords = ["Estado:", "Horario", "UID:", "Log:", "Result"]
    
    print(f"--- Searching in {filename} ---")
    try:
        # Try utf-16 first (PowerShell default) then utf-8 then cp1252
        encodings = ['utf-16', 'utf-8', 'cp1252']
        content = None
        
        for enc in encodings:
            try:
                with open(filename, 'r', encoding=enc) as f:
                    content = f.readlines()
                print(f"Read with encoding: {enc}")
                break
            except UnicodeError:
                continue
                
        if content is None:
            print("Could not read file with standard encodings.")
            return

        for line in content:
            for kw in keywords:
                if kw in line:
                    print(line.strip())
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    grep_file()
