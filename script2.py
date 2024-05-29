import sys

#Functie pentru a inversa sirul

def main():
    input_data = sys.stdin.read().strip()
    
    output_data = input_data[::-1]
    
    print(output_data)

if __name__ == "__main__":
    main()