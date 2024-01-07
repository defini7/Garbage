from csv import reader, DictReader
from sys import argv


def main():
    if len(argv) < 3:
        print('Usage: dna.py database.csv sequence.txt')
        exit(1)

    # read the dna sequence from the file
    with open(argv[2]) as dna_file:
        for row in reader(dna_file):
            dna_list = row

    # store it in a string
    dna = dna_list[0]

    # create a dictionary where we will store the sequences we intend to count
    sequences = {}

    # extract the sequences from the database into a list
    with open(argv[1]) as people_file:
        for row in reader(people_file):
            dna_sequences = row
            dna_sequences.pop(0)
            break

    # copy the list in a dictionary where the genes are the keys
    for item in dna_sequences:
        sequences[item] = 1

    # iterate trough the dna sequence, when it finds repetitions of the values from sequence dictionary it counts them
    for key in sequences:
        temp, temp_max, l = 0, 0, len(key)
        
        for i in range(len(dna)):
            
            # after having counted a sequence it skips at the end of it to avoid counting again
            while temp > 0:
                temp -= 1
                continue

            # if the segment of dna corresponds to the key and there is a repetition of it we start counting
            if dna[i: i + l] == key:
                while dna[i - l: i] == dna[i: i + l]:
                    temp += 1
                    i += l

                # it compares the value to the previous longest sequence and if it is longer it overrides it
                if temp > temp_max:
                    temp_max = temp

        # store the longest sequences in the dictionary using the correspondent key
        sequences[key] += temp_max

    # open and iterate trough the database of people treating each one like a dictionary so it can compare to the sequences one
    with open(argv[1], newline='') as people_file:
        for person in DictReader(people_file):
            
            # compares the sequences to every person and prints name before leaving the program if there is a match
            match = sum(sequences[dna] == int(person[dna]) for dna in sequences)

            if match == len(sequences):
                print(person['name'])
                exit(0)

        print('No match')
    
if __name__ == '__main__':
    main()
