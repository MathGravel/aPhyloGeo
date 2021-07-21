import subprocess
import os
import re
import pandas as pd

def menuGetTrees():
    while True:
        count = input("How many climatic data tree will be used?: ")
        if not count.isnumeric():
            print("This is not a number.")
        elif int(count) < 1:
            print("The number cannot be lower than 1.")
        else:
            # VALIDER LE FORMAT NEWICK??
            try:
                names = []
                for i in range(int(count)):
                    name = input("Name of the tree file (" + str(i+1) + "): " )
                    open(name, "r")
                    names.append(name)
            except:
                    print("This file does not exist or is empty.")
                    continue
            break
    return names


def getBootstrapThreshold():
    valide = False
    while not valide:
        threshold = input("Enter the bootstrap value threshold between 0 and 100%: ")
        valide = threshold.isnumeric() and int(threshold) < 100 and int(threshold) > 0
        if not valide:
            print("Error, it must be a number between 1 and 100.")
        else:
            return threshold


def getRfThreshold():
    valide = False
    while not valide:
        threshold = input("Enter the Robinson and Foulds distance threshold between 0 and 100%: ")
        valide = threshold.isnumeric() and int(threshold) < 100 and int(threshold) > 0
        if not valide:
            print("Error, it must be a number between 1 and 100.")
        else:
            return int(threshold)


def getSlidingWindowSize():
    while True:
        size = input("Sliding window size: ")
        try:
            size = int(size)
        except Exception:
            print("The window size must be a number.")
            continue
        if(size <= 0):
            print("The window size must be between greater than 0.")
        else:
            break
    return size

def getStepSize():
    while True:
        count = input("Step count: ")
        try:
            count = int(count)
        except Exception:
            print("The step count must be a number.")
            continue
        if(count <= 0):
            print("The window size must be between greater than 0.")
        else:
            return count


def slidingWindow(window_size=0, step=0):
    # Permet d'avoir le nombre de lignes totales dans le fichier
    try:
        f = open("infile", "r")
        line_count = -1
        for line in f:
            if line != "\n":
                line_count += 1
        f.close()
        f = open("infile", "r").read()
        # premier nombre de la premiere ligne du fichier represente le nbr de sequences
        num_seq = int((f.split("\n")[0]).split(" ")[0])
        # second nombre de la premiere ligne du fichier represente la longueur des sequences
        longueur = int((f.split("\n")[0]).split(" ")[1])
        # permet d'obtenir le nbr de lignes qui compose chaque sequence
        no_line = int(line_count/num_seq)

        # Recupere la sequence pour chaque variante
        with open("outfile", "w") as out:
            depart = 1
            fin = depart + no_line
            # on connait la longueur de chaque sequence, donc on va recuperer chaque sequence et le retranscrire sur un autre fichier separes par un \n entre chaque
            for i in range(0, int(num_seq)):
                f = open("infile", "r")
                lines_to_read = range(depart, fin)
                for position, line in enumerate(f):
                    if position in lines_to_read:
                        out.write(line)
                out.write("\n")
                depart = fin
                fin = depart + no_line
        out.close()

        # on cree un fichier out qui contient chaque sequence sans espaces et on enregistre dans une list le nom en ordre des sequences
        with open("outfile", "r") as out, open("out", "w") as f:
            sequences = out.read().split("\n\n")
            list_names = []
            for seq in sequences:
                s = seq.replace("\n", " ").split(" ")
                if s[0] != "":
                    list_names.append(s[0])
                s_line = s[1:len(seq)]
                for line in s_line:
                    if line != "":
                        f.write(line)
                f.write("\n")
        out.close()
        f.close()

        # slide the window along the sequence
        debut = 0
        fin = debut + window_size
        while fin <= longueur:
            index = 0 # YA MOYEN ICI DE LE OUTPUT DANS LE BON DOSSIER
            with open("out", "r") as f, open("output/windows/" + str(debut) + "_" + str(fin), "w") as out:
                out.write(str(num_seq) + " " + str(window_size) + "\n")
                for line in f:
                    if line != "\n":
                        espece = list_names[index]
                        nbr_espaces = 11 - len(espece)
                        out.write(espece)
                        for i in range(nbr_espaces):
                            out.write(" ")
                        out.write(line[debut:fin] + "\n")
                        index = index + 1
            out.close()
            f.close()
            debut = debut + step
            fin = fin + step
    except:
        print("An error occurred.")

    # clean up
    os.system("rm out outfile infile")


def validateOptionMenu(window_size, step_size, bootstrap_threshold, rf_threshold, data_names):
    print('===============================================')
    print('Please select an option among the following: ')
    print('===============================================')
    print('1. Use the whole DNA sequences')
    print('2. Study specific genes of SARS-CoV-2')
    while True:
        option = input("Please enter 1 or 2: ")
        if option == '1':
            createReferencePhylogeneticTree(window_size, step_size, bootstrap_threshold, rf_threshold, data_names)
            break
        elif option == '2':
            displayGenesOption(window_size, step_size,
                               bootstrap_threshold, rf_threshold, data_names)
            break
        else:
            print('This is not a valid option.')


def displayGenesOption(window_size, step_size, bootstrap_threshold, rf_threshold, data_names):
    options = {"1": "ORF1ab", "2": "S", "3": "ORF3a", "4": "ORF3b", "5": "E", "6": "M",
               "7": "ORF6", "8": "ORF7a", "9": "ORF7b", "10": "ORF8", "11": "N", "12": "ORF10"}

    print("================================================================================")
    print("Choose among the following genes to analyze seperated by spaces (ex: 1 8 11): ")
    print("================================================================================")
    for number, gene in options.items():
        print(number, ":", gene)
    while True:
        values = input()
        values = values.split()
        # d'abord verifier que toutes les valeurs sont valides
        valides = False
        for value in values:
            if options.get(value) == None:
                print("This is not a valid input. Example of usage: 1 5 12. ")
                valides = False
                break
            else:
                valides = True
        if valides:
            for value in values:
                option = options.get(value)
                if option == "ORF1ab":
                    createPhylogeneticTree(option, 'ATGGAGAGCC(.*)TAACAACTAA', 
                            window_size, step_size, bootstrap_threshold, rf_threshold, data_names)
                if option == "S":
                    createPhylogeneticTree(option, 'ATGTTTGTTT(.*)TTACACATAA',
                            window_size, step_size, bootstrap_threshold, rf_threshold, data_names)
                if option == "ORF3a":
                    createPhylogeneticTree(option, 'ATGGATTTGT(.*)GCCTTTGTAA',
                            window_size, step_size, bootstrap_threshold, rf_threshold, data_names)
                if option == "ORF3b":
                    createPhylogeneticTree(option, 'ATGAGGCTTT(.*)GCCTTTGTAA',
                            window_size, step_size, bootstrap_threshold, rf_threshold, data_names)
                if option == "E":
                    createPhylogeneticTree(option, 'ATGTACTCAT(.*)TCTGGTCTAA',
                            window_size, step_size, bootstrap_threshold, rf_threshold, data_names)
                if option == "M":
                    createPhylogeneticTree(option, 'ATG[GT]CAGATT(.*)TGTACAGTAA',
                            window_size, step_size, bootstrap_threshold, rf_threshold, data_names)
                if option == "ORF6":
                    createPhylogeneticTree(option, 'ATGTTTCATC(.*)GATTGA[CT]TAA',
                            window_size, step_size, bootstrap_threshold, rf_threshold, data_names)
                if option == "ORF7a":
                    createPhylogeneticTree(option, 'ATGAAAATTAT(.*)GACAGAATGA',
                            window_size, step_size, bootstrap_threshold, rf_threshold, data_names)
                if option == "ORF7b":
                    createPhylogeneticTree(
                        option, 'ATGATTGAACTTTCATTAATTGACTTCTATTTGTGCTTTTTAGCCTTTCTGCTATTCCTTGTTTTAATTATGCTTATTATCTTTTGGTTCTCACTTGAACTGCAAGATCATAATGAAACTTGTCACGCCTAA',
                                window_size, step_size, bootstrap_threshold, rf_threshold, data_names)
                if option == "ORF8":
                    createPhylogeneticTree(
                        option, 'ATGAAATTTCTTGTTTT(.*)TTT[TC]ATCTAA',
                                window_size, step_size, bootstrap_threshold, rf_threshold, data_names)
                if option == "N":
                    createPhylogeneticTree(
                        option, 'ATGTCT[CG][AT][TA]AAT(.*)TCAGGCCTAA',
                                window_size, step_size, bootstrap_threshold, rf_threshold)
                if option == "ORF10":
                    createPhylogeneticTree(option, 'ATGGGCTATA(.*)TCTCACATAG', 
                            window_size, step_size, bootstrap_threshold, rf_threshold, data_names)
            break

def menu():
    # try:
        names = menuGetTrees()
        bootstrap_threshold = getBootstrapThreshold()
        rf_threshold = getRfThreshold()
        window_size = getSlidingWindowSize()
        step_size = getStepSize()
        validateOptionMenu(window_size, step_size, bootstrap_threshold, rf_threshold, names)
    # except:
    #     print("An error has occured.")


def getGene(gene, pattern): 
    sequences_file = open("output/reference_gene/reference_gene.fasta", "r").read()
    list_of_sequences = sequences_file.split(">")
    s = pattern
    directory_name = gene + "_gene"
    file_name = gene + "_gene.fasta"
    path = os.path.join("output", directory_name, file_name)
    new_file = open(path, "w")
    for index in range(len(list_of_sequences)):
        if list_of_sequences[index] == "":
            continue
        name = list_of_sequences[index].split("\n")[0]
        gene_sequence = list_of_sequences[index].replace("\n", "")
        gene_sequence = (re.search(s, gene_sequence).group())
        new_file.writelines(">" + name + "\n")
        new_file.writelines(gene_sequence + "\n")

    new_file.close()


def createReferencePhylogeneticTree(window_size, step_size, bootstrap_threshold, rf_threshold, data_names):
    gene = 'reference'
    changeNameSequences()
    number_seq = alignSequences(gene)
    slidingWindow(window_size, step_size)
    files = os.listdir("output/windows")
    for file in files:
        os.system("cp output/windows/" + file + " infile")
        createBoostrap(gene)
        createDistanceMatrix(gene)
        createUnrootedTree(gene)
        createConsensusTree(gene)
        bootstrap_average = calculateAverageBootstrap()
        # on ne tient pas en consideration l'arbre cree, on le supprime
        if bootstrap_average < float(bootstrap_threshold):
            subprocess.call(["rm", "outtree"])
        else: 
            for tree in data_names:
                calculateRfDistance(tree)
                rfn = standardizedRfDistance(number_seq)
                if rfn <= rf_threshold:
                    # dans ce cas, on cree les arbres par raxml
                    runRaxML(file, gene, tree)
                else:
                    os.system("rm outfile")


def createPhylogeneticTree(gene, pattern, window_size, step_size, bootstrap_threshold, rf_threshold, data_names):
    gene = gene
    changeNameSequences()
    getGene(gene, pattern)
    number_seq = alignSequences(gene)
    slidingWindow(window_size, step_size)
    files = os.listdir("output/windows")
    for file in files:
        os.system("cp output/windows/" + file + " infile")
        createBoostrap(gene)
        createDistanceMatrix(gene)
        createUnrootedTree(gene)
        createConsensusTree(gene)
        bootstrap_average = calculateAverageBootstrap()
        # on ne tient pas en consideration l'arbre cree, on le supprime
        if bootstrap_average < float(bootstrap_threshold):
            subprocess.call(["rm", "outtree"])
        else:
            for tree in data_names:
                calculateRfDistance(tree)
                rfn = standardizedRfDistance(18)
                if rfn <= rf_threshold:
                    # dans ce cas, on cree les arbres par raxml
                    runRaxML(file, gene, tree)
                else:
                    os.system("rm outfile")

def alignSequences(gene):
    sequences_file_name = gene + '_gene.fasta'
    directory_name = gene + '_gene'
    file_path = os.path.join('output', directory_name, sequences_file_name)
    subprocess.call(["./exec/muscle", "-in", file_path, "-physout", "infile", "-maxiters", "1", "-diags"])
    f = open("infile", "r").read()
    number_seq = int(f.split()[0])
    return number_seq


def createBoostrap(gene):
    os.system("./exec/seqboot < input_files/bootstrap_input.txt")
    subprocess.call(["mv", "outfile", "infile"])


def getDissimilaritiesMatrix(nom_fichier_csv,column_with_specimen_name, column_to_search, outfile_name):
    df = pd.read_csv(nom_fichier_csv)
    # creation d'une liste contenant les noms des specimens et les temperatures min
    meteo_data = df[column_to_search].tolist()
    nom_var = df[column_with_specimen_name].tolist()
    nbr_seq = len(nom_var)
    # ces deux valeurs seront utiles pour la normalisation
    max_value = 0  
    min_value = 0

    # premiere boucle qui permet de calculer une matrice pour chaque sequence
    temp_tab = []
    for e in range(nbr_seq):
        # une liste qui va contenir toutes les distances avant normalisation
        temp_list = []
        for i in range(nbr_seq):        
            maximum = max(float(meteo_data[e]), float(meteo_data[i]))
            minimum = min(float(meteo_data[e]), float(meteo_data[i]))
            distance = maximum - minimum
            temp_list.append(float("{:.6f}".format(distance)))

        # permet de trouver la valeur maximale et minimale pour la donnee meteo et ensuite d'ajouter la liste temporaire a un tableau
        if max_value < max(temp_list):
            max_value = max(temp_list)
        if min_value > min(temp_list):
            min_value = min(temp_list)
        temp_tab.append(temp_list)
    
    # ecriture des matrices normalisees dans les fichiers respectifs
    with open(outfile_name, "w") as f:
        f.write("   " + str(len(nom_var)) + "\n")
        for j in range(nbr_seq):
            f.write(nom_var[j])
            # petite boucle pour imprimer le bon nbr d'espaces
            for espace in range(11-len(nom_var[j])):
                f.write(" ")
            for k in range(nbr_seq):
                # la normalisation se fait selon la formule suivante: (X - Xmin)/(Xmax - Xmin)
                f.write("{:.6f}".format((temp_tab[j][k] - min_value)/(max_value - min_value)) + " ")
            f.write("\n")
    subprocess.call(["rm", "outfile"]) # clean up


def createDistanceMatrix(gene):
    os.system("./exec/dnadist < input_files/dnadist_input.txt")
    subprocess.call(["mv", "outfile", "infile"])

def createUnrootedTree(gene):
    os.system("./exec/neighbor < input_files/neighbor_input.txt")
    subprocess.call(["rm", "infile", "outfile"])
    subprocess.call(["mv", "outtree", "intree"])


def createConsensusTree(gene):
    os.system("./exec/consense < input_files/input.txt")
    subprocess.call(["rm", "intree", "outfile"])

def calculateAverageBootstrap():
    total = 0
    f = open("outtree", "r").read()
    numbers = re.findall(r'\d+[.]\d+', f)
    for number in numbers:
        total = total + float(number)
    average = total / len(numbers)
    return average

def calculateRfDistance(tree):
    os.system("cat " + tree +" >> infile && cat outtree >> infile")
    os.system("./exec/rf infile outfile tmp matrix")

def standardizedRfDistance(number_seq):
    # clean up the repository
    subprocess.call(["rm", "infile", "matrix", "outtree", "tmp"])
    # find the rf
    f = open("outfile", "r").read()
    words = re.split(r'[ \n]', f)
    for i in range(len(words)):
        if words[i] == "=":
            rf = int(words[i+1])
            normalized_rf = (rf/(2*number_seq-6))*100
            return normalized_rf


def runRaxML(aligned_file, gene, tree):
    current_dir = os.getcwd()
    file_name = os.path.basename(aligned_file + "_" + tree)
    input_path = os.path.join(current_dir, "output", "windows", aligned_file)
    output_path = os.path.join(current_dir, "output", gene + "_gene")
    os.system("./exec/raxmlHPC -s " + input_path + " -n " + file_name + " -w " + output_path + " -N autoMRE -m GTRGAMMA -x 123 -f a -p 123")
    # clean up
    subprocess.call(["rm", output_path + "RAxML_info.*"])
    subprocess.call(["rm", output_path + "RAxML_bootstrap.*"])
    subprocess.call(["make", "clean"])


# def addToCsv():



if __name__ == '__main__':
    menu()
