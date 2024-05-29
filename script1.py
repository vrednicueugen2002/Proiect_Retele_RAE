import sys

#Functie pentru a face literele mari

def main():
    input_data = sys.stdin.read().strip()
    
    output_data = input_data.upper()
    
    print(output_data)

if __name__ == "__main__":
    main()